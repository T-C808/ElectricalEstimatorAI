from __future__ import annotations

import uuid
from decimal import Decimal
from typing import Any, TypeVar

from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import FileResponse
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session, selectinload

from app.core.config import get_settings
from app.db.session import get_db
from app.exports.export_service import (
    create_client_pdf,
    create_internal_csv,
    create_supplier_csv,
    resolve_export_path,
)
from app.models import (
    Assembly,
    AssemblyLabor,
    AssemblyMaterial,
    AssemblyRule,
    Attachment,
    Customer,
    Estimate,
    EstimateAssembly,
    EstimateExport,
    EstimateLineItem,
    Job,
    LaborUnit,
    MarginProfile,
    Material,
)
from app.schemas import (
    AssemblyCreate,
    AssemblyDetailRead,
    AssemblyRead,
    AssemblyUpdate,
    AttachmentCreate,
    AttachmentRead,
    CustomerCreate,
    CustomerRead,
    CustomerUpdate,
    EstimateAssemblyCreate,
    EstimateAssemblyRead,
    EstimateAssemblyUpdate,
    EstimateCalculationResponse,
    EstimateCreate,
    EstimateDetailRead,
    EstimateExportRead,
    EstimateLineItemCreate,
    EstimateLineItemRead,
    EstimateLineItemUpdate,
    EstimateRead,
    EstimateTotals,
    EstimateUpdate,
    HealthResponse,
    JobCreate,
    JobRead,
    JobUpdate,
    LaborUnitCreate,
    LaborUnitRead,
    LaborUnitUpdate,
    MarginProfileCreate,
    MarginProfileRead,
    MarginProfileUpdate,
    MaterialCreate,
    MaterialRead,
    MaterialUpdate,
)
from app.services.estimate_service import (
    EstimateServiceError,
    EstimateValidationError,
    calculate_estimate,
    load_estimate_detail,
)
from app.services.seed import seed_database

api_router = APIRouter()
ModelT = TypeVar("ModelT")


@api_router.get("/health", response_model=HealthResponse)
def health() -> dict[str, str]:
    return {"status": "ok"}


@api_router.post("/dev/seed")
def seed_dev_data(db: Session = Depends(get_db)) -> dict[str, str]:
    if get_settings().app_env == "production":
        raise HTTPException(status_code=404, detail="Seed endpoint is unavailable")
    seed_database(db)
    return {"status": "seeded"}


@api_router.get("/customers", response_model=list[CustomerRead])
def list_customers(db: Session = Depends(get_db)) -> list[Customer]:
    return list(db.scalars(select(Customer).order_by(Customer.updated_at.desc())))


@api_router.post("/customers", response_model=CustomerRead, status_code=201)
def create_customer(payload: CustomerCreate, db: Session = Depends(get_db)) -> Customer:
    customer = Customer(**payload.model_dump())
    db.add(customer)
    _commit(db)
    db.refresh(customer)
    return customer


@api_router.get("/customers/{customer_id}", response_model=CustomerRead)
def get_customer(customer_id: uuid.UUID, db: Session = Depends(get_db)) -> Customer:
    return _get_or_404(db, Customer, customer_id, "Customer")


@api_router.patch("/customers/{customer_id}", response_model=CustomerRead)
def update_customer(
    customer_id: uuid.UUID, payload: CustomerUpdate, db: Session = Depends(get_db)
) -> Customer:
    customer = _get_or_404(db, Customer, customer_id, "Customer")
    _apply_update(customer, payload.model_dump(exclude_unset=True))
    _commit(db)
    db.refresh(customer)
    return customer


@api_router.delete("/customers/{customer_id}", status_code=204)
def delete_customer(customer_id: uuid.UUID, db: Session = Depends(get_db)) -> None:
    customer = _get_or_404(db, Customer, customer_id, "Customer")
    has_jobs = db.scalar(select(Job.id).where(Job.customer_id == customer_id))
    if has_jobs:
        raise HTTPException(status_code=400, detail="Cannot delete a customer with jobs")
    db.delete(customer)
    _commit(db)


@api_router.get("/jobs", response_model=list[JobRead])
def list_jobs(db: Session = Depends(get_db)) -> list[Job]:
    return list(db.scalars(select(Job).order_by(Job.updated_at.desc())))


@api_router.post("/jobs", response_model=JobRead, status_code=201)
def create_job(payload: JobCreate, db: Session = Depends(get_db)) -> Job:
    _get_or_404(db, Customer, payload.customer_id, "Customer")
    job = Job(**payload.model_dump())
    db.add(job)
    _commit(db)
    db.refresh(job)
    return job


@api_router.get("/jobs/{job_id}", response_model=JobRead)
def get_job(job_id: uuid.UUID, db: Session = Depends(get_db)) -> Job:
    return _get_or_404(db, Job, job_id, "Job")


@api_router.patch("/jobs/{job_id}", response_model=JobRead)
def update_job(job_id: uuid.UUID, payload: JobUpdate, db: Session = Depends(get_db)) -> Job:
    job = _get_or_404(db, Job, job_id, "Job")
    data = payload.model_dump(exclude_unset=True)
    if "customer_id" in data:
        _get_or_404(db, Customer, data["customer_id"], "Customer")
    _apply_update(job, data)
    _commit(db)
    db.refresh(job)
    return job


@api_router.delete("/jobs/{job_id}", status_code=204)
def delete_job(job_id: uuid.UUID, db: Session = Depends(get_db)) -> None:
    job = _get_or_404(db, Job, job_id, "Job")
    db.delete(job)
    _commit(db)


@api_router.get("/customers/{customer_id}/jobs", response_model=list[JobRead])
def list_customer_jobs(customer_id: uuid.UUID, db: Session = Depends(get_db)) -> list[Job]:
    _get_or_404(db, Customer, customer_id, "Customer")
    return list(
        db.scalars(
            select(Job).where(Job.customer_id == customer_id).order_by(Job.created_at.desc())
        )
    )


@api_router.get("/jobs/{job_id}/attachments", response_model=list[AttachmentRead])
def list_attachments(job_id: uuid.UUID, db: Session = Depends(get_db)) -> list[Attachment]:
    _get_or_404(db, Job, job_id, "Job")
    return list(db.scalars(select(Attachment).where(Attachment.job_id == job_id)))


@api_router.post("/jobs/{job_id}/attachments", response_model=AttachmentRead, status_code=201)
def create_attachment(
    job_id: uuid.UUID, payload: AttachmentCreate, db: Session = Depends(get_db)
) -> Attachment:
    _get_or_404(db, Job, job_id, "Job")
    attachment = Attachment(job_id=job_id, **payload.model_dump())
    db.add(attachment)
    _commit(db)
    db.refresh(attachment)
    return attachment


@api_router.delete("/attachments/{attachment_id}", status_code=204)
def delete_attachment(attachment_id: uuid.UUID, db: Session = Depends(get_db)) -> None:
    attachment = _get_or_404(db, Attachment, attachment_id, "Attachment")
    db.delete(attachment)
    _commit(db)


@api_router.get("/materials", response_model=list[MaterialRead])
def list_materials(
    q: str | None = None,
    category: str | None = None,
    supplier: str | None = None,
    active: bool | None = None,
    db: Session = Depends(get_db),
) -> list[Material]:
    stmt = select(Material)
    if q:
        stmt = stmt.where(Material.name.ilike(f"%{q}%") | Material.sku.ilike(f"%{q}%"))
    if category:
        stmt = stmt.where(Material.category == category)
    if supplier:
        stmt = stmt.where(Material.supplier == supplier)
    if active is not None:
        stmt = stmt.where(Material.active == active)
    return list(db.scalars(stmt.order_by(Material.sku)))


@api_router.post("/materials", response_model=MaterialRead, status_code=201)
def create_material(payload: MaterialCreate, db: Session = Depends(get_db)) -> Material:
    material = Material(**payload.model_dump())
    db.add(material)
    _commit(db)
    db.refresh(material)
    return material


@api_router.get("/materials/{material_id}", response_model=MaterialRead)
def get_material(material_id: uuid.UUID, db: Session = Depends(get_db)) -> Material:
    return _get_or_404(db, Material, material_id, "Material")


@api_router.patch("/materials/{material_id}", response_model=MaterialRead)
def update_material(
    material_id: uuid.UUID, payload: MaterialUpdate, db: Session = Depends(get_db)
) -> Material:
    material = _get_or_404(db, Material, material_id, "Material")
    _apply_update(material, payload.model_dump(exclude_unset=True))
    _commit(db)
    db.refresh(material)
    return material


@api_router.delete("/materials/{material_id}", status_code=204)
def delete_material(material_id: uuid.UUID, db: Session = Depends(get_db)) -> None:
    material = _get_or_404(db, Material, material_id, "Material")
    material.active = False
    _commit(db)


@api_router.post("/materials/import-csv")
def import_materials_csv_stub() -> dict[str, str]:
    return {"status": "not_implemented", "detail": "CSV import is stubbed for V1."}


@api_router.get("/labor-units", response_model=list[LaborUnitRead])
def list_labor_units(db: Session = Depends(get_db)) -> list[LaborUnit]:
    return list(db.scalars(select(LaborUnit).order_by(LaborUnit.code)))


@api_router.post("/labor-units", response_model=LaborUnitRead, status_code=201)
def create_labor_unit(payload: LaborUnitCreate, db: Session = Depends(get_db)) -> LaborUnit:
    labor = LaborUnit(**payload.model_dump())
    db.add(labor)
    _commit(db)
    db.refresh(labor)
    return labor


@api_router.get("/labor-units/{labor_unit_id}", response_model=LaborUnitRead)
def get_labor_unit(labor_unit_id: uuid.UUID, db: Session = Depends(get_db)) -> LaborUnit:
    return _get_or_404(db, LaborUnit, labor_unit_id, "Labor unit")


@api_router.patch("/labor-units/{labor_unit_id}", response_model=LaborUnitRead)
def update_labor_unit(
    labor_unit_id: uuid.UUID, payload: LaborUnitUpdate, db: Session = Depends(get_db)
) -> LaborUnit:
    labor = _get_or_404(db, LaborUnit, labor_unit_id, "Labor unit")
    _apply_update(labor, payload.model_dump(exclude_unset=True))
    _commit(db)
    db.refresh(labor)
    return labor


@api_router.delete("/labor-units/{labor_unit_id}", status_code=204)
def delete_labor_unit(labor_unit_id: uuid.UUID, db: Session = Depends(get_db)) -> None:
    labor = _get_or_404(db, LaborUnit, labor_unit_id, "Labor unit")
    labor.active = False
    _commit(db)


@api_router.get("/margin-profiles", response_model=list[MarginProfileRead])
def list_margin_profiles(db: Session = Depends(get_db)) -> list[MarginProfile]:
    return list(db.scalars(select(MarginProfile).order_by(MarginProfile.name)))


@api_router.post("/margin-profiles", response_model=MarginProfileRead, status_code=201)
def create_margin_profile(
    payload: MarginProfileCreate, db: Session = Depends(get_db)
) -> MarginProfile:
    profile = MarginProfile(**payload.model_dump())
    db.add(profile)
    _commit(db)
    db.refresh(profile)
    return profile


@api_router.get("/margin-profiles/{margin_profile_id}", response_model=MarginProfileRead)
def get_margin_profile(
    margin_profile_id: uuid.UUID, db: Session = Depends(get_db)
) -> MarginProfile:
    return _get_or_404(db, MarginProfile, margin_profile_id, "Margin profile")


@api_router.patch("/margin-profiles/{margin_profile_id}", response_model=MarginProfileRead)
def update_margin_profile(
    margin_profile_id: uuid.UUID, payload: MarginProfileUpdate, db: Session = Depends(get_db)
) -> MarginProfile:
    profile = _get_or_404(db, MarginProfile, margin_profile_id, "Margin profile")
    _apply_update(profile, payload.model_dump(exclude_unset=True))
    _commit(db)
    db.refresh(profile)
    return profile


@api_router.delete("/margin-profiles/{margin_profile_id}", status_code=204)
def delete_margin_profile(margin_profile_id: uuid.UUID, db: Session = Depends(get_db)) -> None:
    profile = _get_or_404(db, MarginProfile, margin_profile_id, "Margin profile")
    profile.active = False
    _commit(db)


@api_router.get("/assemblies", response_model=list[AssemblyRead])
def list_assemblies(
    q: str | None = None,
    category: str | None = None,
    active: bool | None = None,
    db: Session = Depends(get_db),
) -> list[Assembly]:
    stmt = select(Assembly)
    if q:
        stmt = stmt.where(Assembly.name.ilike(f"%{q}%") | Assembly.code.ilike(f"%{q}%"))
    if category:
        stmt = stmt.where(Assembly.category == category)
    if active is not None:
        stmt = stmt.where(Assembly.active == active)
    return list(db.scalars(stmt.order_by(Assembly.code, Assembly.version)))


@api_router.post("/assemblies", response_model=AssemblyDetailRead, status_code=201)
def create_assembly(payload: AssemblyCreate, db: Session = Depends(get_db)) -> Assembly:
    data = payload.model_dump()
    base_materials = data.pop("base_materials")
    base_labor = data.pop("base_labor")
    rules = data.pop("rules")
    assembly = Assembly(**data)
    db.add(assembly)
    db.flush()
    _replace_assembly_children(db, assembly, base_materials, base_labor, rules)
    _commit(db)
    return _load_assembly_detail(db, assembly.id)


@api_router.get("/assemblies/{assembly_id}", response_model=AssemblyDetailRead)
def get_assembly(assembly_id: uuid.UUID, db: Session = Depends(get_db)) -> Assembly:
    return _load_assembly_detail(db, assembly_id)


@api_router.patch("/assemblies/{assembly_id}", response_model=AssemblyDetailRead)
def update_assembly(
    assembly_id: uuid.UUID, payload: AssemblyUpdate, db: Session = Depends(get_db)
) -> Assembly:
    assembly = _get_or_404(db, Assembly, assembly_id, "Assembly")
    _apply_update(assembly, payload.model_dump(exclude_unset=True))
    _commit(db)
    return _load_assembly_detail(db, assembly.id)


@api_router.delete("/assemblies/{assembly_id}", status_code=204)
def delete_assembly(assembly_id: uuid.UUID, db: Session = Depends(get_db)) -> None:
    assembly = _get_or_404(db, Assembly, assembly_id, "Assembly")
    assembly.active = False
    _commit(db)


@api_router.post("/assemblies/seed")
def seed_assemblies(db: Session = Depends(get_db)) -> dict[str, str]:
    seed_database(db)
    return {"status": "seeded"}


@api_router.get("/estimates", response_model=list[EstimateRead])
def list_estimates(db: Session = Depends(get_db)) -> list[Estimate]:
    return list(db.scalars(select(Estimate).order_by(Estimate.updated_at.desc())))


@api_router.post("/jobs/{job_id}/estimates", response_model=EstimateRead, status_code=201)
def create_estimate(
    job_id: uuid.UUID, payload: EstimateCreate, db: Session = Depends(get_db)
) -> Estimate:
    _get_or_404(db, Job, job_id, "Job")
    _get_or_404(db, MarginProfile, payload.margin_profile_id, "Margin profile")
    estimate = Estimate(job_id=job_id, margin_profile_id=payload.margin_profile_id)
    db.add(estimate)
    _commit(db)
    db.refresh(estimate)
    return estimate


@api_router.get("/estimates/{estimate_id}", response_model=EstimateDetailRead)
def get_estimate(estimate_id: uuid.UUID, db: Session = Depends(get_db)) -> Estimate:
    try:
        return load_estimate_detail(db, estimate_id)
    except EstimateServiceError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc


@api_router.patch("/estimates/{estimate_id}", response_model=EstimateRead)
def update_estimate(
    estimate_id: uuid.UUID, payload: EstimateUpdate, db: Session = Depends(get_db)
) -> Estimate:
    estimate = _get_or_404(db, Estimate, estimate_id, "Estimate")
    data = payload.model_dump(exclude_unset=True)
    if "margin_profile_id" in data:
        _get_or_404(db, MarginProfile, data["margin_profile_id"], "Margin profile")
    _apply_update(estimate, data)
    _commit(db)
    db.refresh(estimate)
    return estimate


@api_router.delete("/estimates/{estimate_id}", status_code=204)
def delete_estimate(estimate_id: uuid.UUID, db: Session = Depends(get_db)) -> None:
    estimate = _get_or_404(db, Estimate, estimate_id, "Estimate")
    db.delete(estimate)
    _commit(db)


@api_router.get("/estimates/{estimate_id}/assemblies", response_model=list[EstimateAssemblyRead])
def list_estimate_assemblies(
    estimate_id: uuid.UUID, db: Session = Depends(get_db)
) -> list[EstimateAssembly]:
    _get_or_404(db, Estimate, estimate_id, "Estimate")
    return list(
        db.scalars(
            select(EstimateAssembly)
            .where(EstimateAssembly.estimate_id == estimate_id)
            .options(selectinload(EstimateAssembly.assembly))
            .order_by(EstimateAssembly.created_at)
        )
    )


@api_router.post(
    "/estimates/{estimate_id}/assemblies", response_model=EstimateAssemblyRead, status_code=201
)
def add_estimate_assembly(
    estimate_id: uuid.UUID, payload: EstimateAssemblyCreate, db: Session = Depends(get_db)
) -> EstimateAssembly:
    _get_or_404(db, Estimate, estimate_id, "Estimate")
    assembly = _get_or_404(db, Assembly, payload.assembly_id, "Assembly")
    estimate_assembly = EstimateAssembly(
        estimate_id=estimate_id,
        assembly_id=assembly.id,
        assembly_code=assembly.code,
        assembly_version=assembly.version,
        parameters=payload.parameters,
    )
    db.add(estimate_assembly)
    _commit(db)
    return _load_estimate_assembly(db, estimate_assembly.id)


@api_router.patch(
    "/estimates/{estimate_id}/assemblies/{estimate_assembly_id}",
    response_model=EstimateAssemblyRead,
)
def update_estimate_assembly(
    estimate_id: uuid.UUID,
    estimate_assembly_id: uuid.UUID,
    payload: EstimateAssemblyUpdate,
    db: Session = Depends(get_db),
) -> EstimateAssembly:
    item = _load_estimate_assembly(db, estimate_assembly_id)
    if item.estimate_id != estimate_id:
        raise HTTPException(status_code=404, detail="Estimate assembly not found")
    _apply_update(item, payload.model_dump(exclude_unset=True))
    _commit(db)
    return _load_estimate_assembly(db, item.id)


@api_router.delete("/estimates/{estimate_id}/assemblies/{estimate_assembly_id}", status_code=204)
def delete_estimate_assembly(
    estimate_id: uuid.UUID, estimate_assembly_id: uuid.UUID, db: Session = Depends(get_db)
) -> None:
    item = _load_estimate_assembly(db, estimate_assembly_id)
    if item.estimate_id != estimate_id:
        raise HTTPException(status_code=404, detail="Estimate assembly not found")
    db.delete(item)
    _commit(db)


@api_router.post("/estimates/{estimate_id}/calculate", response_model=EstimateCalculationResponse)
def calculate_estimate_endpoint(
    estimate_id: uuid.UUID, db: Session = Depends(get_db)
) -> dict[str, Any]:
    try:
        estimate = calculate_estimate(db, estimate_id)
        db.commit()
        estimate = load_estimate_detail(db, estimate.id)
    except EstimateServiceError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
    except EstimateValidationError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    assumptions = [note.note for note in estimate.notes if note.note_type == "assumption"]
    exclusions = [note.note for note in estimate.notes if note.note_type == "exclusion"]
    return {
        "estimate_id": estimate.id,
        "status": estimate.status,
        "totals": EstimateTotals(
            material_subtotal=estimate.material_subtotal,
            labor_subtotal=estimate.labor_subtotal,
            equipment_subtotal=estimate.equipment_subtotal,
            subcontractor_subtotal=estimate.subcontractor_subtotal,
            fee_subtotal=estimate.fee_subtotal,
            overhead_total=estimate.overhead_total,
            profit_total=estimate.profit_total,
            contingency_total=estimate.contingency_total,
            tax_total=estimate.tax_total,
            grand_total=estimate.grand_total,
        ),
        "line_items": estimate.line_items,
        "assumptions": assumptions,
        "exclusions": exclusions,
        "review_flags": estimate.review_flags,
    }


@api_router.post(
    "/estimates/{estimate_id}/line-items", response_model=EstimateLineItemRead, status_code=201
)
def create_manual_line_item(
    estimate_id: uuid.UUID, payload: EstimateLineItemCreate, db: Session = Depends(get_db)
) -> EstimateLineItem:
    _get_or_404(db, Estimate, estimate_id, "Estimate")
    line = EstimateLineItem(
        estimate_id=estimate_id,
        source_type="manual",
        source_id=None,
        **_manual_line_data(payload.model_dump()),
    )
    db.add(line)
    _commit(db)
    db.refresh(line)
    return line


@api_router.patch(
    "/estimates/{estimate_id}/line-items/{line_item_id}", response_model=EstimateLineItemRead
)
def update_manual_line_item(
    estimate_id: uuid.UUID,
    line_item_id: uuid.UUID,
    payload: EstimateLineItemUpdate,
    db: Session = Depends(get_db),
) -> EstimateLineItem:
    line = _get_or_404(db, EstimateLineItem, line_item_id, "Line item")
    if line.estimate_id != estimate_id or line.source_type != "manual":
        raise HTTPException(status_code=404, detail="Manual line item not found")
    data = payload.model_dump(exclude_unset=True)
    for key, value in data.items():
        setattr(line, key, value)
    _recalculate_manual_line(line)
    _commit(db)
    db.refresh(line)
    return line


@api_router.delete("/estimates/{estimate_id}/line-items/{line_item_id}", status_code=204)
def delete_manual_line_item(
    estimate_id: uuid.UUID, line_item_id: uuid.UUID, db: Session = Depends(get_db)
) -> None:
    line = _get_or_404(db, EstimateLineItem, line_item_id, "Line item")
    if line.estimate_id != estimate_id or line.source_type != "manual":
        raise HTTPException(status_code=404, detail="Manual line item not found")
    db.delete(line)
    _commit(db)


@api_router.post("/estimates/{estimate_id}/exports/supplier-csv", response_model=EstimateExportRead)
def export_supplier_csv(estimate_id: uuid.UUID, db: Session = Depends(get_db)) -> EstimateExport:
    return create_supplier_csv(db, estimate_id)


@api_router.post("/estimates/{estimate_id}/exports/internal-csv", response_model=EstimateExportRead)
def export_internal_csv(estimate_id: uuid.UUID, db: Session = Depends(get_db)) -> EstimateExport:
    return create_internal_csv(db, estimate_id)


@api_router.post("/estimates/{estimate_id}/exports/client-pdf", response_model=EstimateExportRead)
def export_client_pdf(estimate_id: uuid.UUID, db: Session = Depends(get_db)) -> EstimateExport:
    return create_client_pdf(db, estimate_id)


@api_router.get("/estimates/{estimate_id}/exports", response_model=list[EstimateExportRead])
def list_exports(estimate_id: uuid.UUID, db: Session = Depends(get_db)) -> list[EstimateExport]:
    _get_or_404(db, Estimate, estimate_id, "Estimate")
    return list(
        db.scalars(
            select(EstimateExport)
            .where(EstimateExport.estimate_id == estimate_id)
            .order_by(EstimateExport.created_at.desc())
        )
    )


@api_router.get("/exports/{export_id}/download")
def download_export(export_id: uuid.UUID, db: Session = Depends(get_db)) -> FileResponse:
    export = _get_or_404(db, EstimateExport, export_id, "Export")
    if not export.storage_key:
        raise HTTPException(status_code=404, detail="Export file is unavailable")
    path = resolve_export_path(export.storage_key)
    if not path.exists():
        raise HTTPException(status_code=404, detail="Export file is missing")
    return FileResponse(path, filename=export.file_name)


def _get_or_404[ModelT](db: Session, model: type[ModelT], item_id: uuid.UUID, label: str) -> ModelT:
    item = db.get(model, item_id)
    if not item:
        raise HTTPException(status_code=404, detail=f"{label} not found")
    return item


def _commit(db: Session) -> None:
    try:
        db.commit()
    except IntegrityError as exc:
        db.rollback()
        raise HTTPException(
            status_code=400, detail="Unique or required field constraint failed"
        ) from exc


def _apply_update(instance: Any, data: dict[str, Any]) -> None:
    for key, value in data.items():
        setattr(instance, key, value)


def _load_assembly_detail(db: Session, assembly_id: uuid.UUID) -> Assembly:
    assembly = db.scalar(
        select(Assembly)
        .where(Assembly.id == assembly_id)
        .options(
            selectinload(Assembly.materials).selectinload(AssemblyMaterial.material),
            selectinload(Assembly.labor).selectinload(AssemblyLabor.labor_unit),
            selectinload(Assembly.rules),
        )
    )
    if not assembly:
        raise HTTPException(status_code=404, detail="Assembly not found")
    return assembly


def _replace_assembly_children(
    db: Session,
    assembly: Assembly,
    base_materials: list[dict[str, Any]],
    base_labor: list[dict[str, Any]],
    rules: list[dict[str, Any]],
) -> None:
    assembly.materials.clear()
    assembly.labor.clear()
    assembly.rules.clear()
    for material_data in base_materials:
        material = db.scalar(select(Material).where(Material.sku == material_data["sku"]))
        if not material:
            raise HTTPException(
                status_code=400, detail=f"Material not found: {material_data['sku']}"
            )
        assembly.materials.append(
            AssemblyMaterial(
                material=material,
                quantity_formula=material_data.get("quantity_formula", "1"),
                unit=material_data.get("unit") or material.unit,
                notes=material_data.get("notes"),
            )
        )
    for labor_data in base_labor:
        labor = db.scalar(select(LaborUnit).where(LaborUnit.code == labor_data["code"]))
        if not labor:
            raise HTTPException(
                status_code=400, detail=f"Labor unit not found: {labor_data['code']}"
            )
        assembly.labor.append(
            AssemblyLabor(
                labor_unit=labor,
                hours_formula=labor_data.get("hours_formula", "base_hours"),
                notes=labor_data.get("notes"),
            )
        )
    for rule_data in rules:
        assembly.rules.append(
            AssemblyRule(
                name=rule_data.get("name", rule_data.get("id", "Rule")), rule_json=rule_data
            )
        )


def _load_estimate_assembly(db: Session, estimate_assembly_id: uuid.UUID) -> EstimateAssembly:
    item = db.scalar(
        select(EstimateAssembly)
        .where(EstimateAssembly.id == estimate_assembly_id)
        .options(selectinload(EstimateAssembly.assembly))
    )
    if not item:
        raise HTTPException(status_code=404, detail="Estimate assembly not found")
    return item


def _manual_line_data(data: dict[str, Any]) -> dict[str, Any]:
    qty = Decimal(str(data.get("quantity", "1")))
    unit_cost = Decimal(str(data.get("unit_cost", "0")))
    unit_sell = Decimal(str(data.get("unit_sell", "0")))
    labor_hours = data.get("labor_hours")
    if data["line_type"] == "labor" and labor_hours is None:
        labor_hours = qty
    return {
        **data,
        "quantity": qty,
        "unit_cost": unit_cost,
        "unit_sell": unit_sell,
        "total_cost": qty * unit_cost,
        "total_sell": qty * unit_sell,
        "labor_hours": labor_hours,
        "margin_percent": None,
    }


def _recalculate_manual_line(line: EstimateLineItem) -> None:
    line.total_cost = line.quantity * line.unit_cost
    line.total_sell = line.quantity * line.unit_sell
    if line.line_type == "labor" and line.labor_hours is None:
        line.labor_hours = line.quantity
