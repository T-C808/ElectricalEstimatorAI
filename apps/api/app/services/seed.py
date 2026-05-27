from __future__ import annotations

from decimal import Decimal
from typing import Any

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.db.session import SessionLocal
from app.models import (
    Assembly,
    AssemblyLabor,
    AssemblyMaterial,
    AssemblyRule,
    LaborUnit,
    MarginProfile,
    Material,
)

DEFAULT_MARGIN_PROFILE = {
    "name": "Default Small Contractor Margin",
    "material_markup_percent": Decimal("0.25"),
    "labor_rate_per_hour": Decimal("125.00"),
    "overhead_percent": Decimal("0.10"),
    "profit_percent": Decimal("0.15"),
    "contingency_percent": Decimal("0.05"),
    "tax_percent": Decimal("0.00"),
    "minimum_margin_percent": Decimal("0.10"),
    "active": True,
}

MATERIALS = [
    ("ATS-600-BYPASS", "600A Automatic Transfer Switch with Bypass", "ATS", "each", "18500.00"),
    ("ATS-400", "400A Automatic Transfer Switch", "ATS", "each", "9800.00"),
    ("PANEL-NEMA-3R", "NEMA 3R Panelboard Allowance", "Panel", "each", "4200.00"),
    ("PANEL-NEMA-3RX", "NEMA 3RX Panelboard Allowance", "Panel", "each", "5200.00"),
    ("CONDUIT-EMT-2IN", "2 inch EMT conduit", "Conduit", "ft", "4.75"),
    ("CONDUIT-PVC-2IN", "2 inch PVC conduit", "Conduit", "ft", "3.60"),
    ("CONDUIT-RIGID-2IN", "2 inch rigid conduit", "Conduit", "ft", "12.50"),
    ("FEEDER-CONDUCTOR-600A", "600A feeder conductor allowance", "Wire", "ft", "14.50"),
    ("GROUND-LUG-KIT", "Grounding lug kit", "Grounding", "kit", "185.00"),
    ("LABEL-KIT-ELECTRICAL", "Electrical label kit", "Labels", "kit", "95.00"),
    ("PULL-BOX-ALLOWANCE", "Pull box allowance", "Boxes", "each", "650.00"),
]

LABOR_UNITS = [
    (
        "INSTALL-ATS-600",
        "Install 600A ATS",
        "Set, mount, and prepare 600A ATS for terminations.",
        "16",
        "2",
        "1",
    ),
    (
        "INSTALL-ATS-400",
        "Install 400A ATS",
        "Set, mount, and prepare 400A ATS for terminations.",
        "12",
        "2",
        "1",
    ),
    ("INSTALL-PANEL", "Install panelboard", "Install panelboard allowance.", "10", "2", "1"),
    (
        "CONDUIT-INSTALL-PER-FT",
        "Install conduit per foot",
        "Generic conduit install labor per foot.",
        "0.08",
        "1",
        "1",
    ),
    (
        "PULL-FEEDER-PER-FT",
        "Pull feeder conductors per foot",
        "Feeder pulling labor per route foot.",
        "0.06",
        "2",
        "1",
    ),
    (
        "TERMINATE-FEEDERS-600A",
        "Terminate 600A feeders",
        "Terminate feeder conductors at equipment.",
        "8",
        "2",
        "1",
    ),
    (
        "SHUTDOWN-COORD",
        "Shutdown coordination",
        "Coordinate customer/utility shutdown window.",
        "4",
        "1",
        "1",
    ),
    (
        "NETA-SUPPORT",
        "NETA testing support",
        "Electrical contractor support for third-party testing.",
        "8",
        "1",
        "1",
    ),
    (
        "GROUNDING-BONDING",
        "Grounding and bonding allowance",
        "Grounding and bonding labor allowance.",
        "6",
        "1",
        "1",
    ),
]

COMMON_PARAMETERS = [
    {"name": "service_size_amps", "type": "number", "required": True},
    {"name": "feeder_length_ft", "type": "number", "required": True},
    {
        "name": "conduit_type",
        "type": "enum",
        "options": ["EMT", "PVC", "RIGID"],
        "required": True,
    },
    {"name": "conductor_count", "type": "number", "required": True, "default": 4},
    {"name": "conduit_count", "type": "number", "required": True, "default": 1},
    {"name": "waste_factor", "type": "number", "required": True, "default": 1.1},
    {"name": "shutdown_required", "type": "boolean", "required": True, "default": False},
    {"name": "neta_testing_required", "type": "boolean", "required": True, "default": False},
    {"name": "existing_equipment_known", "type": "boolean", "required": True, "default": False},
    {
        "name": "utility_coordination_required",
        "type": "boolean",
        "required": False,
        "default": False,
    },
    {
        "name": "generator_interconnection_included",
        "type": "boolean",
        "required": False,
        "default": False,
    },
]

SHUTDOWN_RULE = {
    "id": "shutdown-coordination-required",
    "name": "Shutdown coordination required",
    "when": {"field": "shutdown_required", "operator": "equals", "value": True},
    "actions": [
        {"type": "add_labor", "labor_code": "SHUTDOWN-COORD", "hours": 4},
        {
            "type": "require_review",
            "flag_code": "SHUTDOWN_REQUIRED",
            "severity": "warning",
            "message": (
                "Shutdown required. Confirm schedule, customer impact, and utility requirements."
            ),
        },
    ],
}

NETA_RULE = {
    "id": "neta-testing-selected",
    "name": "NETA testing selected",
    "when": {"field": "neta_testing_required", "operator": "equals", "value": True},
    "actions": [
        {"type": "add_labor", "labor_code": "NETA-SUPPORT", "hours": 8},
        {
            "type": "add_exclusion",
            "note": "Third-party NETA testing fees are excluded unless separately listed.",
        },
        {
            "type": "require_review",
            "flag_code": "NETA_TESTING_SELECTED",
            "severity": "warning",
            "message": "NETA testing selected. Confirm third-party testing scope and fees.",
        },
    ],
}

RIGID_RULE = {
    "id": "rigid-conduit-labor-factor",
    "name": "Rigid conduit labor factor",
    "when": {"field": "conduit_type", "operator": "equals", "value": "RIGID"},
    "actions": [
        {"type": "multiply_labor", "target": "CONDUIT-INSTALL-PER-FT", "factor": 1.35},
        {
            "type": "add_assumption",
            "note": "Rigid conduit selected; labor increased for installation difficulty.",
        },
    ],
}


def _assembly(
    code: str,
    name: str,
    category: str,
    base_materials: list[dict[str, str]],
    base_labor: list[dict[str, str]],
    assumptions: list[str],
    exclusions: list[str],
    rules: list[dict[str, Any]] | None = None,
    parameters: list[dict[str, Any]] | None = None,
) -> dict[str, Any]:
    return {
        "code": code,
        "name": name,
        "version": 1,
        "category": category,
        "parameters": parameters or COMMON_PARAMETERS,
        "base_materials": base_materials,
        "base_labor": base_labor,
        "assumptions": assumptions,
        "exclusions": exclusions,
        "rules": rules or [],
    }


ASSEMBLIES = [
    _assembly(
        "ATS-600-BYPASS",
        "600A ATS Install with Bypass",
        "ATS",
        [
            {"sku": "ATS-600-BYPASS", "quantity_formula": "1", "unit": "each"},
            {"sku": "GROUND-LUG-KIT", "quantity_formula": "1", "unit": "kit"},
            {"sku": "LABEL-KIT-ELECTRICAL", "quantity_formula": "1", "unit": "kit"},
        ],
        [
            {"code": "INSTALL-ATS-600", "hours_formula": "base_hours"},
            {"code": "TERMINATE-FEEDERS-600A", "hours_formula": "base_hours"},
        ],
        [
            "Existing gear is suitable for reuse unless otherwise noted.",
            "Normal working hours unless shutdown coordination is selected.",
            "Estimate assumes clear working access to equipment.",
        ],
        [
            "Permits and AHJ fees unless explicitly included.",
            "Utility company fees.",
            "Engineering studies unless explicitly included.",
            "Unforeseen code corrections.",
        ],
        [SHUTDOWN_RULE, NETA_RULE],
    ),
    _assembly(
        "ATS-400",
        "400A ATS Install",
        "ATS",
        [
            {"sku": "ATS-400", "quantity_formula": "1", "unit": "each"},
            {"sku": "GROUND-LUG-KIT", "quantity_formula": "1", "unit": "kit"},
            {"sku": "LABEL-KIT-ELECTRICAL", "quantity_formula": "1", "unit": "kit"},
        ],
        [{"code": "INSTALL-ATS-400", "hours_formula": "base_hours"}],
        [
            "Existing gear is suitable for reuse unless otherwise noted.",
            "Estimate assumes clear working access to equipment.",
        ],
        ["Permits, utility fees, and unforeseen code corrections are excluded."],
        [SHUTDOWN_RULE, NETA_RULE],
    ),
    _assembly(
        "PANEL-NEMA-3R",
        "NEMA 3R Panel Upgrade",
        "Panel",
        [
            {"sku": "PANEL-NEMA-3R", "quantity_formula": "1", "unit": "each"},
            {"sku": "LABEL-KIT-ELECTRICAL", "quantity_formula": "1", "unit": "kit"},
        ],
        [
            {"code": "INSTALL-PANEL", "hours_formula": "base_hours"},
            {"code": "GROUNDING-BONDING", "hours_formula": "base_hours"},
        ],
        ["NEMA 3R panel allowance is owner-editable and based on placeholder pricing."],
        ["Unforeseen feeder changes are excluded unless separately listed."],
    ),
    _assembly(
        "PANEL-NEMA-3RX",
        "NEMA 3RX Panel Upgrade",
        "Panel",
        [
            {"sku": "PANEL-NEMA-3RX", "quantity_formula": "1", "unit": "each"},
            {"sku": "LABEL-KIT-ELECTRICAL", "quantity_formula": "1", "unit": "kit"},
        ],
        [
            {"code": "INSTALL-PANEL", "hours_formula": "base_hours * 1.1"},
            {"code": "GROUNDING-BONDING", "hours_formula": "base_hours"},
        ],
        ["NEMA 3RX panel allowance is owner-editable and based on placeholder pricing."],
        ["Unforeseen feeder changes are excluded unless separately listed."],
    ),
    _assembly(
        "FEEDER-EMT",
        "Feeder Run - EMT",
        "Feeder",
        [
            {"sku": "CONDUIT-EMT-2IN", "quantity_formula": "feeder_length_ft * 1.05", "unit": "ft"},
            {
                "sku": "FEEDER-CONDUCTOR-600A",
                "quantity_formula": "feeder_length_ft * conductor_count * waste_factor",
                "unit": "ft",
            },
        ],
        [
            {"code": "CONDUIT-INSTALL-PER-FT", "hours_formula": "base_hours * feeder_length_ft"},
            {"code": "PULL-FEEDER-PER-FT", "hours_formula": "base_hours * feeder_length_ft"},
        ],
        [
            "Feeder route length is based on provided field input.",
            "Standard supports and fittings are included as an allowance only.",
        ],
        ["Core drilling, trenching, and concrete repair are excluded unless separately listed."],
        [SHUTDOWN_RULE, NETA_RULE],
    ),
    _assembly(
        "FEEDER-PVC",
        "Feeder Run - PVC",
        "Feeder",
        [
            {"sku": "CONDUIT-PVC-2IN", "quantity_formula": "feeder_length_ft * 1.05", "unit": "ft"},
            {
                "sku": "FEEDER-CONDUCTOR-600A",
                "quantity_formula": "feeder_length_ft * conductor_count * waste_factor",
                "unit": "ft",
            },
        ],
        [
            {"code": "CONDUIT-INSTALL-PER-FT", "hours_formula": "base_hours * feeder_length_ft"},
            {"code": "PULL-FEEDER-PER-FT", "hours_formula": "base_hours * feeder_length_ft"},
        ],
        [
            "Feeder route length is based on provided field input.",
            "PVC conduit selected; estimate assumes installation conditions suitable for PVC.",
        ],
        ["Core drilling, trenching, and concrete repair are excluded unless separately listed."],
        [SHUTDOWN_RULE, NETA_RULE],
    ),
    _assembly(
        "FEEDER-RIGID",
        "Feeder Run - Rigid Conduit",
        "Feeder",
        [
            {
                "sku": "CONDUIT-RIGID-2IN",
                "quantity_formula": "feeder_length_ft * 1.05",
                "unit": "ft",
            },
            {
                "sku": "FEEDER-CONDUCTOR-600A",
                "quantity_formula": "feeder_length_ft * conductor_count * waste_factor",
                "unit": "ft",
            },
        ],
        [
            {"code": "CONDUIT-INSTALL-PER-FT", "hours_formula": "base_hours * feeder_length_ft"},
            {"code": "PULL-FEEDER-PER-FT", "hours_formula": "base_hours * feeder_length_ft"},
        ],
        [
            "Feeder route length is based on provided field input.",
            "Rigid conduit selected; estimate assumes heavier installation conditions.",
        ],
        ["Core drilling, trenching, and concrete repair are excluded unless separately listed."],
        [RIGID_RULE, SHUTDOWN_RULE, NETA_RULE],
    ),
    _assembly(
        "SHUTDOWN-COORD",
        "Shutdown Coordination Allowance",
        "Coordination",
        [],
        [{"code": "SHUTDOWN-COORD", "hours_formula": "base_hours"}],
        [
            "Includes coordination allowance only. Final shutdown schedule requires customer and "
            "utility approval."
        ],
        ["Utility fees and after-hours premiums are excluded unless separately listed."],
        parameters=[],
    ),
    _assembly(
        "NETA-SUPPORT",
        "NETA Testing Support Allowance",
        "Testing",
        [],
        [{"code": "NETA-SUPPORT", "hours_formula": "base_hours"}],
        ["Includes electrical contractor support time only."],
        ["Third-party NETA testing fees are excluded unless separately listed."],
        parameters=[],
    ),
    _assembly(
        "GROUNDING-BONDING",
        "Grounding/Bonding Allowance",
        "Grounding",
        [{"sku": "GROUND-LUG-KIT", "quantity_formula": "1", "unit": "kit"}],
        [{"code": "GROUNDING-BONDING", "hours_formula": "base_hours"}],
        ["Grounding and bonding scope is allowance-based pending field verification."],
        ["Unforeseen grounding electrode system repairs are excluded unless separately listed."],
        parameters=[],
    ),
]


def seed_database(db: Session) -> None:
    _seed_margin_profile(db)
    materials = _seed_materials(db)
    labor_units = _seed_labor_units(db)
    _seed_assemblies(db, materials, labor_units)
    db.commit()


def _seed_margin_profile(db: Session) -> None:
    existing = db.scalar(
        select(MarginProfile).where(MarginProfile.name == DEFAULT_MARGIN_PROFILE["name"])
    )
    if existing:
        for key, value in DEFAULT_MARGIN_PROFILE.items():
            setattr(existing, key, value)
        return
    db.add(MarginProfile(**DEFAULT_MARGIN_PROFILE))


def _seed_materials(db: Session) -> dict[str, Material]:
    materials: dict[str, Material] = {}
    for sku, name, category, unit, unit_cost in MATERIALS:
        material = db.scalar(select(Material).where(Material.sku == sku))
        data = {
            "sku": sku,
            "name": name,
            "category": category,
            "unit": unit,
            "unit_cost": Decimal(unit_cost),
            "default_markup_percent": Decimal("0.25"),
            "supplier": "TBD",
            "manufacturer": "TBD",
            "active": True,
        }
        if material:
            for key, value in data.items():
                setattr(material, key, value)
        else:
            material = Material(**data)
            db.add(material)
        materials[sku] = material
    db.flush()
    return materials


def _seed_labor_units(db: Session) -> dict[str, LaborUnit]:
    labor_units: dict[str, LaborUnit] = {}
    for code, name, description, base_hours, crew_size, difficulty_factor in LABOR_UNITS:
        labor = db.scalar(select(LaborUnit).where(LaborUnit.code == code))
        data = {
            "code": code,
            "name": name,
            "description": description,
            "base_hours": Decimal(base_hours),
            "crew_size": Decimal(crew_size),
            "difficulty_factor": Decimal(difficulty_factor),
            "active": True,
        }
        if labor:
            for key, value in data.items():
                setattr(labor, key, value)
        else:
            labor = LaborUnit(**data)
            db.add(labor)
        labor_units[code] = labor
    db.flush()
    return labor_units


def _seed_assemblies(
    db: Session, materials: dict[str, Material], labor_units: dict[str, LaborUnit]
) -> None:
    for data in ASSEMBLIES:
        assembly = db.scalar(
            select(Assembly).where(
                Assembly.code == data["code"], Assembly.version == data["version"]
            )
        )
        assembly_data = {
            "code": data["code"],
            "name": data["name"],
            "version": data["version"],
            "category": data["category"],
            "parameters": data["parameters"],
            "assumptions": data["assumptions"],
            "exclusions": data["exclusions"],
            "review_flag_rules": [],
            "active": True,
        }
        if assembly:
            for key, value in assembly_data.items():
                setattr(assembly, key, value)
            assembly.materials.clear()
            assembly.labor.clear()
            assembly.rules.clear()
        else:
            assembly = Assembly(**assembly_data)
            db.add(assembly)
        db.flush()

        for material_data in data["base_materials"]:
            assembly.materials.append(
                AssemblyMaterial(
                    material=materials[material_data["sku"]],
                    quantity_formula=material_data["quantity_formula"],
                    unit=material_data["unit"],
                )
            )
        for labor_data in data["base_labor"]:
            assembly.labor.append(
                AssemblyLabor(
                    labor_unit=labor_units[labor_data["code"]],
                    hours_formula=labor_data["hours_formula"],
                )
            )
        for rule in data["rules"]:
            assembly.rules.append(AssemblyRule(name=rule["name"], rule_json=rule, active=True))


def main() -> None:
    with SessionLocal() as db:
        seed_database(db)
    print("Seed data loaded.")


if __name__ == "__main__":
    main()
