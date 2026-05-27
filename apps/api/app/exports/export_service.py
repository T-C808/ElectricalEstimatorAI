from __future__ import annotations

import csv
import uuid
from datetime import UTC, datetime
from pathlib import Path

from reportlab.lib import colors
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.platypus import Paragraph, SimpleDocTemplate, Spacer, Table, TableStyle
from sqlalchemy.orm import Session

from app.core.config import get_settings
from app.models import Estimate, EstimateExport
from app.services.estimate_service import REQUIRED_DISCLAIMER, load_estimate_detail

SUPPLIER_COLUMNS = ["SKU", "Description", "Quantity", "Unit", "Manufacturer", "Supplier", "Notes"]
INTERNAL_COLUMNS = [
    "Line Type",
    "Source Type",
    "Source Assembly",
    "SKU",
    "Description",
    "Quantity",
    "Unit",
    "Unit Cost",
    "Unit Sell",
    "Total Cost",
    "Total Sell",
    "Labor Hours",
    "Rule Applied",
    "Notes",
]


def create_supplier_csv(db: Session, estimate_id: uuid.UUID) -> EstimateExport:
    estimate = load_estimate_detail(db, estimate_id)
    path, file_name, storage_key = _export_path(estimate, "supplier-bom", "csv")
    material_meta = _snapshot_material_meta(estimate)
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=SUPPLIER_COLUMNS)
        writer.writeheader()
        for line in estimate.line_items:
            if line.line_type not in {"material", "equipment"}:
                continue
            meta = material_meta.get(line.sku or "", {})
            writer.writerow(
                {
                    "SKU": line.sku or "",
                    "Description": line.description,
                    "Quantity": str(line.quantity),
                    "Unit": line.unit or "",
                    "Manufacturer": meta.get("manufacturer") or "",
                    "Supplier": meta.get("supplier") or "",
                    "Notes": line.notes or "",
                }
            )
    return _record_export(db, estimate.id, "supplier_csv", file_name, storage_key)


def create_internal_csv(db: Session, estimate_id: uuid.UUID) -> EstimateExport:
    estimate = load_estimate_detail(db, estimate_id)
    path, file_name, storage_key = _export_path(estimate, "internal-bom", "csv")
    assembly_sources = {
        item["estimate_assembly_id"]: item["code"]
        for item in estimate.snapshot.get("assemblies", [])
    }
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=INTERNAL_COLUMNS)
        writer.writeheader()
        for line in estimate.line_items:
            source_id = str(line.source_id) if line.source_id else ""
            writer.writerow(
                {
                    "Line Type": line.line_type,
                    "Source Type": line.source_type,
                    "Source Assembly": assembly_sources.get(source_id, ""),
                    "SKU": line.sku or "",
                    "Description": line.description,
                    "Quantity": str(line.quantity),
                    "Unit": line.unit or "",
                    "Unit Cost": str(line.unit_cost),
                    "Unit Sell": str(line.unit_sell),
                    "Total Cost": str(line.total_cost),
                    "Total Sell": str(line.total_sell),
                    "Labor Hours": str(line.labor_hours or ""),
                    "Rule Applied": line.notes or "",
                    "Notes": line.notes or "",
                }
            )
    return _record_export(db, estimate.id, "internal_csv", file_name, storage_key)


def create_client_pdf(db: Session, estimate_id: uuid.UUID) -> EstimateExport:
    estimate = load_estimate_detail(db, estimate_id)
    path, file_name, storage_key = _export_path(estimate, "client", "pdf")
    styles = getSampleStyleSheet()
    story = [
        Paragraph("Electrical Estimate", styles["Title"]),
        Paragraph("Contractor: Electrical Estimator V1", styles["Normal"]),
        Spacer(1, 12),
        Paragraph(f"Customer: {estimate.job.customer.company_name}", styles["Heading2"]),
        Paragraph(f"Job: {estimate.job.job_name}", styles["Normal"]),
        Paragraph(f"Site: {estimate.job.site_address or 'Not provided'}", styles["Normal"]),
        Spacer(1, 12),
        Paragraph("Price Summary", styles["Heading2"]),
        _summary_table(estimate),
        Spacer(1, 12),
        Paragraph("Included Work", styles["Heading2"]),
    ]
    for line in estimate.line_items:
        if line.line_type in {"material", "labor", "equipment", "fee"}:
            story.append(
                Paragraph(
                    f"{line.description}: {line.quantity} {line.unit or ''}", styles["Normal"]
                )
            )

    assumptions = [note.note for note in estimate.notes if note.note_type == "assumption"]
    exclusions = [note.note for note in estimate.notes if note.note_type == "exclusion"]
    story.extend([Spacer(1, 12), Paragraph("Assumptions", styles["Heading2"])])
    for note in assumptions or ["No additional assumptions listed."]:
        story.append(Paragraph(f"- {note}", styles["Normal"]))
    story.extend([Spacer(1, 12), Paragraph("Exclusions", styles["Heading2"])])
    for note in exclusions or ["No additional exclusions listed."]:
        story.append(Paragraph(f"- {note}", styles["Normal"]))

    story.extend(
        [
            Spacer(1, 12),
            Paragraph("Review and Disclaimer", styles["Heading2"]),
            Paragraph(REQUIRED_DISCLAIMER, styles["Normal"]),
            Spacer(1, 24),
            Paragraph("Approval Signature: ________________________________", styles["Normal"]),
        ]
    )
    SimpleDocTemplate(str(path), pagesize=letter, pageCompression=0).build(story)
    return _record_export(db, estimate.id, "client_pdf", file_name, storage_key)


def resolve_export_path(storage_key: str) -> Path:
    return _storage_root() / storage_key


def _summary_table(estimate: Estimate) -> Table:
    rows = [
        [
            "Material and equipment",
            f"${estimate.material_subtotal + estimate.equipment_subtotal:,.2f}",
        ],
        ["Labor", f"${estimate.labor_subtotal:,.2f}"],
        ["Fees/allowances", f"${estimate.fee_subtotal + estimate.subcontractor_subtotal:,.2f}"],
        ["Overhead", f"${estimate.overhead_total:,.2f}"],
        ["Profit", f"${estimate.profit_total:,.2f}"],
        ["Contingency", f"${estimate.contingency_total:,.2f}"],
        ["Tax", f"${estimate.tax_total:,.2f}"],
        ["Total estimate", f"${estimate.grand_total:,.2f}"],
    ]
    table = Table(rows, colWidths=[260, 140])
    table.setStyle(
        TableStyle(
            [
                ("BACKGROUND", (0, -1), (-1, -1), colors.lightgrey),
                ("GRID", (0, 0), (-1, -1), 0.25, colors.grey),
                ("ALIGN", (1, 0), (1, -1), "RIGHT"),
                ("FONTNAME", (0, -1), (-1, -1), "Helvetica-Bold"),
            ]
        )
    )
    return table


def _record_export(
    db: Session, estimate_id: uuid.UUID, export_type: str, file_name: str, storage_key: str
) -> EstimateExport:
    export = EstimateExport(
        estimate_id=estimate_id,
        export_type=export_type,
        file_name=file_name,
        storage_key=storage_key,
    )
    db.add(export)
    db.commit()
    db.refresh(export)
    return export


def _export_path(estimate: Estimate, suffix: str, extension: str) -> tuple[Path, str, str]:
    today = datetime.now(UTC).strftime("%Y%m%d")
    prefix = str(estimate.id)[:8]
    file_name = f"estimate-{prefix}-{today}-{suffix}.{extension}"
    storage_key = f"exports/{file_name}"
    path = _storage_root() / storage_key
    path.parent.mkdir(parents=True, exist_ok=True)
    return path, file_name, storage_key


def _storage_root() -> Path:
    return get_settings().local_storage_path


def _snapshot_material_meta(estimate: Estimate) -> dict[str, dict]:
    return {material["sku"]: material for material in estimate.snapshot.get("materials", [])}
