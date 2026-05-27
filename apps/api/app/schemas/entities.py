from __future__ import annotations

import uuid
from datetime import datetime
from decimal import Decimal
from typing import Any, Literal

from pydantic import BaseModel, ConfigDict, Field

JobStatus = Literal[
    "draft", "estimating", "review_required", "approved", "sent", "won", "lost", "archived"
]
EstimateStatus = Literal[
    "draft", "calculated", "review_required", "approved", "sent", "won", "lost", "archived"
]
LineSourceType = Literal["manual", "assembly", "rule"]
LineItemType = Literal["material", "labor", "equipment", "subcontractor", "fee", "note"]
NoteType = Literal["assumption", "exclusion", "internal_note", "client_note", "disclaimer"]
FlagSeverity = Literal["info", "warning", "critical"]


class OrmModel(BaseModel):
    model_config = ConfigDict(from_attributes=True)


class CustomerBase(BaseModel):
    company_name: str | None = None
    contact_name: str | None = None
    email: str | None = None
    phone: str | None = None
    billing_address: str | None = None
    notes: str | None = None


class CustomerCreate(CustomerBase):
    company_name: str = Field(min_length=1)


class CustomerUpdate(CustomerBase):
    pass


class CustomerRead(CustomerBase, OrmModel):
    id: uuid.UUID
    created_at: datetime
    updated_at: datetime


class JobBase(BaseModel):
    customer_id: uuid.UUID
    job_name: str = Field(min_length=1)
    site_address: str | None = None
    site_contact: str | None = None
    job_type: str | None = None
    status: JobStatus = "draft"
    notes: str | None = None


class JobCreate(JobBase):
    pass


class JobUpdate(BaseModel):
    customer_id: uuid.UUID | None = None
    job_name: str | None = None
    site_address: str | None = None
    site_contact: str | None = None
    job_type: str | None = None
    status: JobStatus | None = None
    notes: str | None = None


class JobRead(JobBase, OrmModel):
    id: uuid.UUID
    created_at: datetime
    updated_at: datetime


class AttachmentCreate(BaseModel):
    file_name: str = Field(min_length=1)
    file_type: str | None = None
    storage_key: str | None = None
    storage_url: str | None = None
    uploaded_by: str | None = None


class AttachmentRead(AttachmentCreate, OrmModel):
    id: uuid.UUID
    job_id: uuid.UUID
    created_at: datetime


class MaterialBase(BaseModel):
    sku: str = Field(min_length=1)
    name: str = Field(min_length=1)
    category: str | None = None
    unit: str = Field(min_length=1)
    unit_cost: Decimal = Field(ge=0)
    default_markup_percent: Decimal = Field(default=Decimal("0"), ge=0)
    supplier: str | None = None
    manufacturer: str | None = None
    active: bool = True


class MaterialCreate(MaterialBase):
    pass


class MaterialUpdate(BaseModel):
    sku: str | None = None
    name: str | None = None
    category: str | None = None
    unit: str | None = None
    unit_cost: Decimal | None = Field(default=None, ge=0)
    default_markup_percent: Decimal | None = Field(default=None, ge=0)
    supplier: str | None = None
    manufacturer: str | None = None
    active: bool | None = None


class MaterialRead(MaterialBase, OrmModel):
    id: uuid.UUID
    created_at: datetime
    updated_at: datetime


class LaborUnitBase(BaseModel):
    code: str = Field(min_length=1)
    name: str = Field(min_length=1)
    description: str | None = None
    base_hours: Decimal = Field(ge=0)
    crew_size: Decimal = Field(default=Decimal("1"), ge=0)
    difficulty_factor: Decimal = Field(default=Decimal("1"), ge=0)
    active: bool = True


class LaborUnitCreate(LaborUnitBase):
    pass


class LaborUnitUpdate(BaseModel):
    code: str | None = None
    name: str | None = None
    description: str | None = None
    base_hours: Decimal | None = Field(default=None, ge=0)
    crew_size: Decimal | None = Field(default=None, ge=0)
    difficulty_factor: Decimal | None = Field(default=None, ge=0)
    active: bool | None = None


class LaborUnitRead(LaborUnitBase, OrmModel):
    id: uuid.UUID
    created_at: datetime
    updated_at: datetime


class MarginProfileBase(BaseModel):
    name: str = Field(min_length=1)
    material_markup_percent: Decimal = Field(ge=0)
    labor_rate_per_hour: Decimal = Field(ge=0)
    overhead_percent: Decimal = Field(default=Decimal("0"), ge=0)
    profit_percent: Decimal = Field(default=Decimal("0"), ge=0)
    contingency_percent: Decimal = Field(default=Decimal("0"), ge=0)
    tax_percent: Decimal = Field(default=Decimal("0"), ge=0)
    minimum_margin_percent: Decimal = Field(default=Decimal("0"), ge=0)
    active: bool = True


class MarginProfileCreate(MarginProfileBase):
    pass


class MarginProfileUpdate(BaseModel):
    name: str | None = None
    material_markup_percent: Decimal | None = Field(default=None, ge=0)
    labor_rate_per_hour: Decimal | None = Field(default=None, ge=0)
    overhead_percent: Decimal | None = Field(default=None, ge=0)
    profit_percent: Decimal | None = Field(default=None, ge=0)
    contingency_percent: Decimal | None = Field(default=None, ge=0)
    tax_percent: Decimal | None = Field(default=None, ge=0)
    minimum_margin_percent: Decimal | None = Field(default=None, ge=0)
    active: bool | None = None


class MarginProfileRead(MarginProfileBase, OrmModel):
    id: uuid.UUID
    created_at: datetime
    updated_at: datetime


class AssemblyMaterialRead(OrmModel):
    id: uuid.UUID
    material_id: uuid.UUID
    quantity_formula: str
    unit: str | None
    notes: str | None
    material: MaterialRead


class AssemblyLaborRead(OrmModel):
    id: uuid.UUID
    labor_unit_id: uuid.UUID
    hours_formula: str
    notes: str | None
    labor_unit: LaborUnitRead


class AssemblyRuleRead(OrmModel):
    id: uuid.UUID
    name: str
    rule_json: dict[str, Any]
    active: bool
    created_at: datetime
    updated_at: datetime


class AssemblyBase(BaseModel):
    code: str = Field(min_length=1)
    name: str = Field(min_length=1)
    version: int = 1
    category: str | None = None
    parameters: list[dict[str, Any]] = Field(default_factory=list)
    assumptions: list[str] = Field(default_factory=list)
    exclusions: list[str] = Field(default_factory=list)
    review_flag_rules: list[dict[str, Any]] = Field(default_factory=list)
    active: bool = True


class AssemblyCreate(AssemblyBase):
    base_materials: list[dict[str, Any]] = Field(default_factory=list)
    base_labor: list[dict[str, Any]] = Field(default_factory=list)
    rules: list[dict[str, Any]] = Field(default_factory=list)


class AssemblyUpdate(BaseModel):
    code: str | None = None
    name: str | None = None
    version: int | None = None
    category: str | None = None
    parameters: list[dict[str, Any]] | None = None
    assumptions: list[str] | None = None
    exclusions: list[str] | None = None
    review_flag_rules: list[dict[str, Any]] | None = None
    active: bool | None = None


class AssemblyRead(AssemblyBase, OrmModel):
    id: uuid.UUID
    created_at: datetime
    updated_at: datetime


class AssemblyDetailRead(AssemblyRead):
    materials: list[AssemblyMaterialRead] = Field(default_factory=list)
    labor: list[AssemblyLaborRead] = Field(default_factory=list)
    rules: list[AssemblyRuleRead] = Field(default_factory=list)


class EstimateCreate(BaseModel):
    margin_profile_id: uuid.UUID


class EstimateUpdate(BaseModel):
    margin_profile_id: uuid.UUID | None = None
    status: EstimateStatus | None = None


class EstimateAssemblyCreate(BaseModel):
    assembly_id: uuid.UUID
    parameters: dict[str, Any] = Field(default_factory=dict)


class EstimateAssemblyUpdate(BaseModel):
    parameters: dict[str, Any] | None = None


class EstimateAssemblyRead(OrmModel):
    id: uuid.UUID
    estimate_id: uuid.UUID
    assembly_id: uuid.UUID
    assembly_code: str
    assembly_version: int
    parameters: dict[str, Any]
    created_at: datetime
    updated_at: datetime
    assembly: AssemblyRead


class EstimateLineItemCreate(BaseModel):
    line_type: LineItemType
    sku: str | None = None
    description: str = Field(min_length=1)
    quantity: Decimal = Decimal("1")
    unit: str | None = None
    unit_cost: Decimal = Decimal("0")
    unit_sell: Decimal = Decimal("0")
    labor_hours: Decimal | None = None
    notes: str | None = None


class EstimateLineItemUpdate(BaseModel):
    line_type: LineItemType | None = None
    sku: str | None = None
    description: str | None = None
    quantity: Decimal | None = None
    unit: str | None = None
    unit_cost: Decimal | None = None
    unit_sell: Decimal | None = None
    labor_hours: Decimal | None = None
    notes: str | None = None


class EstimateLineItemRead(OrmModel):
    id: uuid.UUID
    estimate_id: uuid.UUID
    source_type: LineSourceType
    source_id: uuid.UUID | None
    line_type: LineItemType
    sku: str | None
    description: str
    quantity: Decimal
    unit: str | None
    unit_cost: Decimal
    unit_sell: Decimal
    total_cost: Decimal
    total_sell: Decimal
    labor_hours: Decimal | None
    margin_percent: Decimal | None
    notes: str | None
    created_at: datetime


class EstimateNoteRead(OrmModel):
    id: uuid.UUID
    estimate_id: uuid.UUID
    note_type: NoteType
    note: str
    source_type: str | None
    source_id: uuid.UUID | None
    created_at: datetime


class EstimateReviewFlagRead(OrmModel):
    id: uuid.UUID
    estimate_id: uuid.UUID
    flag_code: str
    severity: FlagSeverity
    message: str
    source_type: str | None
    source_id: uuid.UUID | None
    created_at: datetime


class EstimateExportRead(OrmModel):
    id: uuid.UUID
    estimate_id: uuid.UUID
    export_type: str
    file_name: str
    storage_key: str | None
    created_at: datetime


class EstimateRead(OrmModel):
    id: uuid.UUID
    job_id: uuid.UUID
    margin_profile_id: uuid.UUID
    status: EstimateStatus
    material_subtotal: Decimal
    labor_subtotal: Decimal
    equipment_subtotal: Decimal
    subcontractor_subtotal: Decimal
    fee_subtotal: Decimal
    overhead_total: Decimal
    profit_total: Decimal
    contingency_total: Decimal
    tax_total: Decimal
    grand_total: Decimal
    snapshot: dict[str, Any]
    created_at: datetime
    updated_at: datetime


class EstimateDetailRead(EstimateRead):
    assemblies: list[EstimateAssemblyRead] = Field(default_factory=list)
    line_items: list[EstimateLineItemRead] = Field(default_factory=list)
    notes: list[EstimateNoteRead] = Field(default_factory=list)
    review_flags: list[EstimateReviewFlagRead] = Field(default_factory=list)
    exports: list[EstimateExportRead] = Field(default_factory=list)


class EstimateTotals(BaseModel):
    material_subtotal: Decimal
    labor_subtotal: Decimal
    equipment_subtotal: Decimal
    subcontractor_subtotal: Decimal
    fee_subtotal: Decimal
    overhead_total: Decimal
    profit_total: Decimal
    contingency_total: Decimal
    tax_total: Decimal
    grand_total: Decimal


class EstimateCalculationResponse(BaseModel):
    estimate_id: uuid.UUID
    status: EstimateStatus
    totals: EstimateTotals
    line_items: list[EstimateLineItemRead]
    assumptions: list[str]
    exclusions: list[str]
    review_flags: list[EstimateReviewFlagRead]


class HealthResponse(BaseModel):
    status: str = "ok"
