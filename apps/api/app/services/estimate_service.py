from __future__ import annotations

import uuid
from collections import defaultdict
from datetime import UTC, datetime
from decimal import Decimal, InvalidOperation
from typing import Any

from sqlalchemy import delete, select
from sqlalchemy.orm import Session, selectinload

from app.domain.formula import FormulaError, evaluate_formula
from app.domain.pricing import calculate_totals, labor_sell, material_sell, money, quantity
from app.domain.rules import RuleError, evaluate_condition, target_matches
from app.models import (
    Assembly,
    AssemblyLabor,
    AssemblyMaterial,
    AssemblyRule,
    Estimate,
    EstimateAssembly,
    EstimateLineItem,
    EstimateNote,
    EstimateReviewFlag,
    LaborUnit,
    Material,
)

REQUIRED_DISCLAIMER = (
    "This estimate is based on the information provided and listed assumptions. Final installation "
    "is subject to field verification, applicable code requirements, utility requirements, and AHJ "
    "approval. This estimate is not a substitute for code compliance review or AHJ approval."
)


class EstimateServiceError(ValueError):
    pass


def load_estimate_detail(db: Session, estimate_id: uuid.UUID) -> Estimate:
    estimate = db.scalar(
        select(Estimate)
        .where(Estimate.id == estimate_id)
        .options(
            selectinload(Estimate.job),
            selectinload(Estimate.margin_profile),
            selectinload(Estimate.assemblies)
            .selectinload(EstimateAssembly.assembly)
            .selectinload(Assembly.materials)
            .selectinload(AssemblyMaterial.material),
            selectinload(Estimate.assemblies)
            .selectinload(EstimateAssembly.assembly)
            .selectinload(Assembly.labor)
            .selectinload(AssemblyLabor.labor_unit),
            selectinload(Estimate.assemblies)
            .selectinload(EstimateAssembly.assembly)
            .selectinload(Assembly.rules),
            selectinload(Estimate.line_items),
            selectinload(Estimate.notes),
            selectinload(Estimate.review_flags),
            selectinload(Estimate.exports),
        )
    )
    if not estimate:
        raise EstimateServiceError("Estimate not found")
    return estimate


def calculate_estimate(db: Session, estimate_id: uuid.UUID) -> Estimate:
    estimate = load_estimate_detail(db, estimate_id)
    margin = estimate.margin_profile

    manual_lines = [line for line in estimate.line_items if line.source_type == "manual"]
    db.execute(
        delete(EstimateLineItem).where(
            EstimateLineItem.estimate_id == estimate.id,
            EstimateLineItem.source_type != "manual",
        )
    )
    db.execute(delete(EstimateNote).where(EstimateNote.estimate_id == estimate.id))
    db.execute(delete(EstimateReviewFlag).where(EstimateReviewFlag.estimate_id == estimate.id))
    db.flush()

    lines: list[dict[str, Any]] = []
    notes: dict[str, dict[str, set[str]]] = {
        "assumption": defaultdict(set),
        "exclusion": defaultdict(set),
        "internal_note": defaultdict(set),
        "client_note": defaultdict(set),
        "disclaimer": defaultdict(set),
    }
    flags: dict[str, dict[str, Any]] = {}
    snapshot_rules: list[dict[str, Any]] = []
    snapshot_assemblies: list[dict[str, Any]] = []
    snapshot_materials: dict[str, dict[str, Any]] = {}
    snapshot_labor: dict[str, dict[str, Any]] = {}

    for estimate_assembly in estimate.assemblies:
        assembly = estimate_assembly.assembly
        params = _merge_parameters(assembly.parameters, estimate_assembly.parameters)
        snapshot_assemblies.append(
            {
                "id": str(assembly.id),
                "estimate_assembly_id": str(estimate_assembly.id),
                "code": assembly.code,
                "name": assembly.name,
                "version": assembly.version,
                "parameters": params,
            }
        )

        for text in assembly.assumptions:
            _add_note(notes, "assumption", text, "assembly", str(estimate_assembly.id))
        for text in assembly.exclusions:
            _add_note(notes, "exclusion", text, "assembly", str(estimate_assembly.id))

        _add_required_parameter_flags(assembly, estimate_assembly, params, flags)
        _add_guardrail_flags(assembly, estimate_assembly, params, flags)

        for assembly_material in assembly.materials:
            material = assembly_material.material
            snapshot_materials[material.sku] = _material_snapshot(material)
            context = _formula_context(params)
            try:
                qty = quantity(evaluate_formula(assembly_material.quantity_formula, context))
            except FormulaError as exc:
                _add_flag(
                    flags,
                    f"FORMULA_ERROR_{assembly.code}_{material.sku}",
                    "critical",
                    f"{assembly.code} material formula failed for {material.sku}: {exc}",
                    "assembly",
                    str(estimate_assembly.id),
                )
                qty = Decimal("0")
            lines.append(
                _material_line(
                    material=material,
                    qty=qty,
                    source_type="assembly",
                    source_id=estimate_assembly.id,
                    markup_percent=margin.material_markup_percent,
                    unit=assembly_material.unit or material.unit,
                    notes=assembly_material.notes,
                )
            )

        for assembly_labor in assembly.labor:
            labor_unit = assembly_labor.labor_unit
            snapshot_labor[labor_unit.code] = _labor_snapshot(labor_unit)
            context = _formula_context(
                params,
                base_hours=labor_unit.base_hours,
                crew_size=labor_unit.crew_size,
                difficulty_factor=labor_unit.difficulty_factor,
            )
            try:
                hours = money(evaluate_formula(assembly_labor.hours_formula, context))
            except FormulaError as exc:
                _add_flag(
                    flags,
                    f"FORMULA_ERROR_{assembly.code}_{labor_unit.code}",
                    "critical",
                    f"{assembly.code} labor formula failed for {labor_unit.code}: {exc}",
                    "assembly",
                    str(estimate_assembly.id),
                )
                hours = Decimal("0")
            lines.append(
                _labor_line(
                    labor_unit=labor_unit,
                    hours=hours,
                    source_type="assembly",
                    source_id=estimate_assembly.id,
                    labor_rate=margin.labor_rate_per_hour,
                    notes=assembly_labor.notes,
                )
            )

        for rule in assembly.rules:
            if not rule.active:
                continue
            snapshot_rules.append(
                {
                    "id": str(rule.id),
                    "assembly_code": assembly.code,
                    "name": rule.name,
                    "rule_json": rule.rule_json,
                }
            )
            try:
                if evaluate_condition(rule.rule_json.get("when", {}), params):
                    _apply_rule_actions(
                        db=db,
                        rule=rule,
                        estimate_assembly=estimate_assembly,
                        params=params,
                        lines=lines,
                        notes=notes,
                        flags=flags,
                        labor_rate=margin.labor_rate_per_hour,
                        material_markup_percent=margin.material_markup_percent,
                        snapshot_materials=snapshot_materials,
                        snapshot_labor=snapshot_labor,
                    )
            except (RuleError, FormulaError) as exc:
                _add_flag(
                    flags,
                    f"RULE_ERROR_{rule.rule_json.get('id', rule.id)}",
                    "critical",
                    f"Rule '{rule.name}' failed: {exc}",
                    "rule",
                    str(rule.id),
                )

    if manual_lines:
        _add_flag(
            flags,
            "MANUAL_OVERRIDE_USED",
            "warning",
            "Manual override used. Verify pricing before sending.",
            "manual",
            None,
        )

    all_line_values = lines + [_line_to_dict(line) for line in manual_lines]
    totals = _totals_for_lines(all_line_values, margin)
    _add_margin_floor_flag(flags, all_line_values, margin, totals["grand_total"])

    persisted_lines = [
        EstimateLineItem(estimate_id=estimate.id, **_persistable_line(line)) for line in lines
    ]
    db.add_all(persisted_lines)
    _persist_notes(db, estimate.id, notes)
    _persist_flags(db, estimate.id, flags)

    for key, value in totals.items():
        setattr(estimate, key, value)
    estimate.status = "review_required" if flags else "calculated"
    estimate.snapshot = _jsonable(
        {
            "calculated_at": datetime.now(UTC).isoformat(),
            "margin_profile": {
                "id": str(margin.id),
                "name": margin.name,
                "material_markup_percent": margin.material_markup_percent,
                "labor_rate_per_hour": margin.labor_rate_per_hour,
                "overhead_percent": margin.overhead_percent,
                "profit_percent": margin.profit_percent,
                "contingency_percent": margin.contingency_percent,
                "tax_percent": margin.tax_percent,
                "minimum_margin_percent": margin.minimum_margin_percent,
            },
            "assemblies": snapshot_assemblies,
            "materials": list(snapshot_materials.values()),
            "labor_units": list(snapshot_labor.values()),
            "rules": snapshot_rules,
            "parameters": [item["parameters"] for item in snapshot_assemblies],
            "line_items": all_line_values,
            "totals": totals,
            "assumptions": sorted(notes["assumption"].keys()),
            "exclusions": sorted(notes["exclusion"].keys()),
            "review_flags": list(flags.values()),
            "disclaimer": REQUIRED_DISCLAIMER,
        }
    )

    db.flush()
    db.refresh(estimate)
    return load_estimate_detail(db, estimate.id)


def _merge_parameters(
    definitions: list[dict[str, Any]], provided: dict[str, Any]
) -> dict[str, Any]:
    merged = {
        definition["name"]: definition.get("default")
        for definition in definitions
        if "name" in definition
    }
    merged.update(provided or {})
    return merged


def _formula_context(params: dict[str, Any], **overrides: Decimal) -> dict[str, Any]:
    context = {
        "feeder_length_ft": _decimal_or_default(params.get("feeder_length_ft"), Decimal("0")),
        "conductor_count": _decimal_or_default(params.get("conductor_count"), Decimal("4")),
        "conduit_count": _decimal_or_default(params.get("conduit_count"), Decimal("1")),
        "waste_factor": _decimal_or_default(params.get("waste_factor"), Decimal("1.1")),
        "crew_size": _decimal_or_default(params.get("crew_size"), Decimal("1")),
        "difficulty_factor": _decimal_or_default(params.get("difficulty_factor"), Decimal("1")),
        "base_hours": Decimal("0"),
    }
    context.update(overrides)
    return context


def _decimal_or_default(value: Any, default: Decimal) -> Decimal:
    if value in (None, ""):
        return default
    try:
        return Decimal(str(value))
    except (InvalidOperation, ValueError):
        return default


def _material_line(
    *,
    material: Material,
    qty: Decimal,
    source_type: str,
    source_id: uuid.UUID,
    markup_percent: Decimal,
    unit: str,
    notes: str | None = None,
) -> dict[str, Any]:
    unit_sell = material_sell(material.unit_cost, markup_percent)
    return {
        "source_type": source_type,
        "source_id": source_id,
        "line_type": "material",
        "sku": material.sku,
        "description": material.name,
        "quantity": qty,
        "unit": unit,
        "unit_cost": money(material.unit_cost),
        "unit_sell": unit_sell,
        "total_cost": money(qty * material.unit_cost),
        "total_sell": money(qty * unit_sell),
        "labor_hours": None,
        "margin_percent": markup_percent,
        "notes": notes,
        "manufacturer": material.manufacturer,
        "supplier": material.supplier,
    }


def _labor_line(
    *,
    labor_unit: LaborUnit,
    hours: Decimal,
    source_type: str,
    source_id: uuid.UUID,
    labor_rate: Decimal,
    notes: str | None = None,
) -> dict[str, Any]:
    unit_sell = money(labor_rate)
    return {
        "source_type": source_type,
        "source_id": source_id,
        "line_type": "labor",
        "sku": labor_unit.code,
        "description": labor_unit.name,
        "quantity": hours,
        "unit": "hr",
        "unit_cost": Decimal("0"),
        "unit_sell": unit_sell,
        "total_cost": Decimal("0"),
        "total_sell": labor_sell(hours, labor_rate),
        "labor_hours": hours,
        "margin_percent": None,
        "notes": notes,
    }


def _apply_rule_actions(
    *,
    db: Session,
    rule: AssemblyRule,
    estimate_assembly: EstimateAssembly,
    params: dict[str, Any],
    lines: list[dict[str, Any]],
    notes: dict[str, dict[str, set[str]]],
    flags: dict[str, dict[str, Any]],
    labor_rate: Decimal,
    material_markup_percent: Decimal,
    snapshot_materials: dict[str, dict[str, Any]],
    snapshot_labor: dict[str, dict[str, Any]],
) -> None:
    for action in rule.rule_json.get("actions", []):
        action_type = action.get("type")
        if action_type == "add_material":
            material = db.scalar(select(Material).where(Material.sku == action["material_sku"]))
            if not material:
                raise RuleError(f"Material {action['material_sku']} not found")
            qty = quantity(
                evaluate_formula(action.get("quantity_formula", "1"), _formula_context(params))
            )
            snapshot_materials[material.sku] = _material_snapshot(material)
            lines.append(
                _material_line(
                    material=material,
                    qty=qty,
                    source_type="rule",
                    source_id=rule.id,
                    markup_percent=material_markup_percent,
                    unit=action.get("unit") or material.unit,
                    notes=f"Rule applied: {rule.name}",
                )
            )
        elif action_type == "add_labor":
            labor_unit = db.scalar(select(LaborUnit).where(LaborUnit.code == action["labor_code"]))
            if not labor_unit:
                raise RuleError(f"Labor unit {action['labor_code']} not found")
            if "hours_formula" in action:
                hours = money(
                    evaluate_formula(
                        action["hours_formula"],
                        _formula_context(params, base_hours=labor_unit.base_hours),
                    )
                )
            else:
                hours = money(Decimal(str(action.get("hours", labor_unit.base_hours))))
            snapshot_labor[labor_unit.code] = _labor_snapshot(labor_unit)
            lines.append(
                _labor_line(
                    labor_unit=labor_unit,
                    hours=hours,
                    source_type="rule",
                    source_id=rule.id,
                    labor_rate=labor_rate,
                    notes=f"Rule applied: {rule.name}",
                )
            )
        elif action_type == "multiply_labor":
            factor = Decimal(str(action.get("factor", "1")))
            for line in lines:
                if (
                    line["line_type"] == "labor"
                    and line["source_id"] == estimate_assembly.id
                    and target_matches(line.get("sku"), action.get("target"))
                ):
                    line["labor_hours"] = money(line["labor_hours"] * factor)
                    line["quantity"] = line["labor_hours"]
                    line["total_sell"] = labor_sell(line["labor_hours"], labor_rate)
                    suffix = f"Rule applied: {rule.name}"
                    line["notes"] = f"{line['notes']}; {suffix}" if line.get("notes") else suffix
        elif action_type == "add_note":
            _add_note(
                notes,
                action.get("note_type", "internal_note"),
                action["note"],
                "rule",
                str(rule.id),
            )
        elif action_type == "add_assumption":
            _add_note(notes, "assumption", action["note"], "rule", str(rule.id))
        elif action_type == "add_exclusion":
            _add_note(notes, "exclusion", action["note"], "rule", str(rule.id))
        elif action_type == "require_review":
            _add_flag(
                flags,
                action["flag_code"],
                action.get("severity", "warning"),
                action["message"],
                "rule",
                str(rule.id),
            )
        else:
            raise RuleError(f"Unsupported rule action: {action_type}")


def _add_note(
    notes: dict[str, dict[str, set[str]]],
    note_type: str,
    note: str,
    source_type: str,
    source_id: str | None,
) -> None:
    notes.setdefault(note_type, defaultdict(set))
    notes[note_type][note].add(f"{source_type}:{source_id or ''}")


def _add_flag(
    flags: dict[str, dict[str, Any]],
    flag_code: str,
    severity: str,
    message: str,
    source_type: str | None = None,
    source_id: str | None = None,
) -> None:
    flags.setdefault(
        flag_code,
        {
            "flag_code": flag_code,
            "severity": severity,
            "message": message,
            "source_type": source_type,
            "source_id": source_id,
        },
    )


def _add_required_parameter_flags(
    assembly: Assembly,
    estimate_assembly: EstimateAssembly,
    params: dict[str, Any],
    flags: dict[str, dict[str, Any]],
) -> None:
    for definition in assembly.parameters:
        name = definition.get("name")
        if not definition.get("required") or not name:
            continue
        if params.get(name) in (None, ""):
            _add_flag(
                flags,
                f"MISSING_{name.upper()}",
                "critical",
                f"{name.replace('_', ' ').title()} is missing for {assembly.code}.",
                "assembly",
                str(estimate_assembly.id),
            )


def _add_guardrail_flags(
    assembly: Assembly,
    estimate_assembly: EstimateAssembly,
    params: dict[str, Any],
    flags: dict[str, dict[str, Any]],
) -> None:
    service_size = _decimal_or_default(params.get("service_size_amps"), Decimal("0"))
    if service_size >= Decimal("400"):
        _add_flag(
            flags,
            "SERVICE_SIZE_400A_OR_GREATER",
            "warning",
            "Service size is 400A or greater. Owner review required.",
            "assembly",
            str(estimate_assembly.id),
        )
    if assembly.code.startswith("ATS"):
        _add_flag(
            flags,
            "ATS_INCLUDED",
            "warning",
            "ATS included. Owner review required before customer submission.",
            "assembly",
            str(estimate_assembly.id),
        )
    if params.get("generator_interconnection_included") is True:
        _add_flag(
            flags,
            "GENERATOR_INTERCONNECTION_INCLUDED",
            "warning",
            "Generator interconnection included. Confirm utility and AHJ requirements.",
            "assembly",
            str(estimate_assembly.id),
        )
    if params.get("neta_testing_required") is True:
        _add_flag(
            flags,
            "NETA_TESTING_SELECTED",
            "warning",
            "NETA testing selected. Confirm third-party testing scope and fees.",
            "assembly",
            str(estimate_assembly.id),
        )
    if params.get("shutdown_required") is True:
        _add_flag(
            flags,
            "SHUTDOWN_REQUIRED",
            "warning",
            "Shutdown required. Confirm schedule, customer impact, and utility requirements.",
            "assembly",
            str(estimate_assembly.id),
        )
    if params.get("utility_coordination_required") is True:
        _add_flag(
            flags,
            "UTILITY_COORDINATION_REQUIRED",
            "warning",
            "Utility coordination required. Confirm utility requirements and fees.",
            "assembly",
            str(estimate_assembly.id),
        )
    if params.get("existing_equipment_known") is False:
        _add_flag(
            flags,
            "UNKNOWN_EXISTING_EQUIPMENT",
            "warning",
            "Existing equipment is unknown. Field verification is required.",
            "assembly",
            str(estimate_assembly.id),
        )


def _add_margin_floor_flag(
    flags: dict[str, dict[str, Any]],
    lines: list[dict[str, Any]],
    margin: Any,
    grand_total: Decimal,
) -> None:
    total_cost = sum((line.get("total_cost") or Decimal("0")) for line in lines)
    if grand_total <= 0:
        return
    realized_margin = (grand_total - total_cost) / grand_total
    if realized_margin < margin.minimum_margin_percent:
        _add_flag(
            flags,
            "MARGIN_BELOW_MINIMUM",
            "critical",
            "Calculated margin is below the configured minimum threshold.",
            "estimate",
            None,
        )


def _totals_for_lines(lines: list[dict[str, Any]], margin: Any) -> dict[str, Decimal]:
    by_type = defaultdict(lambda: Decimal("0"))
    for line in lines:
        by_type[line["line_type"]] += line.get("total_sell") or Decimal("0")
    return calculate_totals(
        material_sell_total=by_type["material"],
        labor_sell_total=by_type["labor"],
        equipment_sell_total=by_type["equipment"],
        subcontractor_sell_total=by_type["subcontractor"],
        fee_sell_total=by_type["fee"],
        overhead_percent=margin.overhead_percent,
        profit_percent=margin.profit_percent,
        contingency_percent=margin.contingency_percent,
        tax_percent=margin.tax_percent,
    )


def _persistable_line(line: dict[str, Any]) -> dict[str, Any]:
    allowed = {
        "source_type",
        "source_id",
        "line_type",
        "sku",
        "description",
        "quantity",
        "unit",
        "unit_cost",
        "unit_sell",
        "total_cost",
        "total_sell",
        "labor_hours",
        "margin_percent",
        "notes",
    }
    return {key: value for key, value in line.items() if key in allowed}


def _persist_notes(
    db: Session, estimate_id: uuid.UUID, notes: dict[str, dict[str, set[str]]]
) -> None:
    _add_note(notes, "disclaimer", REQUIRED_DISCLAIMER, "system", None)
    for note_type, values in notes.items():
        for note in values:
            db.add(EstimateNote(estimate_id=estimate_id, note_type=note_type, note=note))


def _persist_flags(db: Session, estimate_id: uuid.UUID, flags: dict[str, dict[str, Any]]) -> None:
    for flag in flags.values():
        source_id = uuid.UUID(flag["source_id"]) if flag.get("source_id") else None
        db.add(
            EstimateReviewFlag(
                estimate_id=estimate_id,
                flag_code=flag["flag_code"],
                severity=flag["severity"],
                message=flag["message"],
                source_type=flag.get("source_type"),
                source_id=source_id,
            )
        )


def _line_to_dict(line: EstimateLineItem) -> dict[str, Any]:
    return {
        "source_type": line.source_type,
        "source_id": str(line.source_id) if line.source_id else None,
        "line_type": line.line_type,
        "sku": line.sku,
        "description": line.description,
        "quantity": line.quantity,
        "unit": line.unit,
        "unit_cost": line.unit_cost,
        "unit_sell": line.unit_sell,
        "total_cost": line.total_cost,
        "total_sell": line.total_sell,
        "labor_hours": line.labor_hours,
        "margin_percent": line.margin_percent,
        "notes": line.notes,
    }


def _material_snapshot(material: Material) -> dict[str, Any]:
    return {
        "id": str(material.id),
        "sku": material.sku,
        "name": material.name,
        "category": material.category,
        "unit": material.unit,
        "unit_cost": material.unit_cost,
        "default_markup_percent": material.default_markup_percent,
        "supplier": material.supplier,
        "manufacturer": material.manufacturer,
    }


def _labor_snapshot(labor_unit: LaborUnit) -> dict[str, Any]:
    return {
        "id": str(labor_unit.id),
        "code": labor_unit.code,
        "name": labor_unit.name,
        "description": labor_unit.description,
        "base_hours": labor_unit.base_hours,
        "crew_size": labor_unit.crew_size,
        "difficulty_factor": labor_unit.difficulty_factor,
    }


def _jsonable(value: Any) -> Any:
    if isinstance(value, Decimal):
        return str(value)
    if isinstance(value, uuid.UUID):
        return str(value)
    if isinstance(value, dict):
        return {key: _jsonable(item) for key, item in value.items()}
    if isinstance(value, list):
        return [_jsonable(item) for item in value]
    return value
