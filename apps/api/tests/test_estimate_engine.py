from __future__ import annotations

from decimal import Decimal

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models import Assembly, Customer, Estimate, EstimateAssembly, Job, MarginProfile, Material
from app.services.estimate_service import calculate_estimate


def _create_estimate(db: Session, assembly_code: str, params: dict) -> Estimate:
    customer = Customer(company_name="Demo Customer", contact_name="Owner")
    db.add(customer)
    db.flush()
    job = Job(customer_id=customer.id, job_name="600A ATS Demo", status="estimating")
    db.add(job)
    db.flush()
    margin = db.scalar(select(MarginProfile).where(MarginProfile.active == True))  # noqa: E712
    assembly = db.scalar(select(Assembly).where(Assembly.code == assembly_code))
    estimate = Estimate(job_id=job.id, margin_profile_id=margin.id)
    db.add(estimate)
    db.flush()
    db.add(
        EstimateAssembly(
            estimate_id=estimate.id,
            assembly_id=assembly.id,
            assembly_code=assembly.code,
            assembly_version=assembly.version,
            parameters=params,
        )
    )
    db.commit()
    return estimate


def test_ats_assembly_generates_totals_flags_and_snapshot(db_session: Session) -> None:
    estimate = _create_estimate(
        db_session,
        "ATS-600-BYPASS",
        {
            "service_size_amps": 600,
            "feeder_length_ft": 125,
            "conduit_type": "EMT",
            "conductor_count": 4,
            "waste_factor": 1.1,
            "shutdown_required": True,
            "neta_testing_required": False,
            "existing_equipment_known": False,
        },
    )

    calculated = calculate_estimate(db_session, estimate.id)
    db_session.commit()

    assert calculated.grand_total > 0
    assert calculated.status == "review_required"
    assert {flag.flag_code for flag in calculated.review_flags} >= {
        "ATS_INCLUDED",
        "SERVICE_SIZE_400A_OR_GREATER",
        "SHUTDOWN_REQUIRED",
        "UNKNOWN_EXISTING_EQUIPMENT",
    }
    assert calculated.snapshot["assemblies"][0]["code"] == "ATS-600-BYPASS"

    ats = db_session.scalar(select(Material).where(Material.sku == "ATS-600-BYPASS"))
    ats.unit_cost = Decimal("1.00")
    db_session.commit()
    original_line = next(line for line in calculated.line_items if line.sku == "ATS-600-BYPASS")
    assert original_line.unit_cost == Decimal("18500.00")


def test_feeder_length_drives_material_quantities(db_session: Session) -> None:
    estimate = _create_estimate(
        db_session,
        "FEEDER-EMT",
        {
            "service_size_amps": 600,
            "feeder_length_ft": 125,
            "conduit_type": "EMT",
            "conductor_count": 4,
            "waste_factor": 1.1,
            "shutdown_required": False,
            "neta_testing_required": False,
            "existing_equipment_known": True,
        },
    )

    calculated = calculate_estimate(db_session, estimate.id)
    conduit = next(line for line in calculated.line_items if line.sku == "CONDUIT-EMT-2IN")
    conductor = next(line for line in calculated.line_items if line.sku == "FEEDER-CONDUCTOR-600A")

    assert conduit.quantity == Decimal("131.250")
    assert conductor.quantity == Decimal("550.000")


def test_rigid_conduit_rule_increases_labor(db_session: Session) -> None:
    estimate = _create_estimate(
        db_session,
        "FEEDER-RIGID",
        {
            "service_size_amps": 600,
            "feeder_length_ft": 100,
            "conduit_type": "RIGID",
            "conductor_count": 4,
            "waste_factor": 1.1,
            "shutdown_required": False,
            "neta_testing_required": False,
            "existing_equipment_known": True,
        },
    )

    calculated = calculate_estimate(db_session, estimate.id)
    conduit_labor = next(
        line for line in calculated.line_items if line.sku == "CONDUIT-INSTALL-PER-FT"
    )
    assert conduit_labor.labor_hours == Decimal("10.80")
    assert "Rigid conduit labor factor" in conduit_labor.notes


def test_neta_adds_labor_exclusion_and_review_flag(db_session: Session) -> None:
    estimate = _create_estimate(
        db_session,
        "ATS-600-BYPASS",
        {
            "service_size_amps": 600,
            "feeder_length_ft": 125,
            "conduit_type": "EMT",
            "conductor_count": 4,
            "waste_factor": 1.1,
            "shutdown_required": False,
            "neta_testing_required": True,
            "existing_equipment_known": True,
        },
    )

    calculated = calculate_estimate(db_session, estimate.id)
    assert any(line.sku == "NETA-SUPPORT" for line in calculated.line_items)
    assert any(flag.flag_code == "NETA_TESTING_SELECTED" for flag in calculated.review_flags)
    assert any("Third-party NETA testing fees" in note.note for note in calculated.notes)
