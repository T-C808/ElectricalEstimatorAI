from __future__ import annotations

from pathlib import Path

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.config import get_settings
from app.exports.export_service import create_client_pdf, create_internal_csv, create_supplier_csv
from app.models import Assembly, Customer, Estimate, EstimateAssembly, Job, MarginProfile
from app.services.estimate_service import calculate_estimate


def _calculated_estimate(db: Session) -> Estimate:
    customer = Customer(company_name="Export Customer")
    db.add(customer)
    db.flush()
    job = Job(customer_id=customer.id, job_name="Export Job")
    db.add(job)
    db.flush()
    margin = db.scalar(select(MarginProfile).where(MarginProfile.active == True))  # noqa: E712
    assembly = db.scalar(select(Assembly).where(Assembly.code == "FEEDER-EMT"))
    estimate = Estimate(job_id=job.id, margin_profile_id=margin.id)
    db.add(estimate)
    db.flush()
    db.add(
        EstimateAssembly(
            estimate_id=estimate.id,
            assembly_id=assembly.id,
            assembly_code=assembly.code,
            assembly_version=assembly.version,
            parameters={
                "service_size_amps": 600,
                "feeder_length_ft": 20,
                "conduit_type": "EMT",
                "conductor_count": 4,
                "waste_factor": 1.1,
                "shutdown_required": False,
                "neta_testing_required": False,
                "existing_equipment_known": True,
            },
        )
    )
    db.commit()
    return calculate_estimate(db, estimate.id)


def test_csv_export_shapes_and_pdf_disclaimer(db_session: Session, tmp_path: Path) -> None:
    get_settings().local_storage_path = tmp_path
    estimate = _calculated_estimate(db_session)

    supplier = create_supplier_csv(db_session, estimate.id)
    internal = create_internal_csv(db_session, estimate.id)
    pdf = create_client_pdf(db_session, estimate.id)

    supplier_text = (tmp_path / supplier.storage_key).read_text()
    internal_text = (tmp_path / internal.storage_key).read_text()
    pdf_bytes = (tmp_path / pdf.storage_key).read_bytes()

    assert "Unit Cost" not in supplier_text
    assert "Labor Hours" not in supplier_text
    assert "Unit Cost" in internal_text
    assert "Labor Hours" in internal_text
    for phrase in ["This estimate is based", "AHJ approval", "code compliance review"]:
        assert phrase.encode() in pdf_bytes
