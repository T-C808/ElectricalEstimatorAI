from __future__ import annotations

import uuid
from datetime import datetime
from decimal import Decimal

from sqlalchemy import (
    JSON,
    Boolean,
    DateTime,
    ForeignKey,
    Numeric,
    String,
    Text,
    UniqueConstraint,
    func,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.types import Uuid

from app.db.base import Base


def uuid_pk() -> Mapped[uuid.UUID]:
    return mapped_column(Uuid(as_uuid=True), primary_key=True, default=uuid.uuid4)


def created_at_column() -> Mapped[datetime]:
    return mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False)


def updated_at_column() -> Mapped[datetime]:
    return mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False
    )


Money = Numeric(12, 2)
Percent = Numeric(8, 4)


class Customer(Base):
    __tablename__ = "customers"

    id: Mapped[uuid.UUID] = uuid_pk()
    company_name: Mapped[str | None] = mapped_column(String(255))
    contact_name: Mapped[str | None] = mapped_column(String(255))
    email: Mapped[str | None] = mapped_column(String(255))
    phone: Mapped[str | None] = mapped_column(String(80))
    billing_address: Mapped[str | None] = mapped_column(Text)
    notes: Mapped[str | None] = mapped_column(Text)
    created_at: Mapped[datetime] = created_at_column()
    updated_at: Mapped[datetime] = updated_at_column()

    jobs: Mapped[list[Job]] = relationship(back_populates="customer", cascade="all, delete-orphan")


class Job(Base):
    __tablename__ = "jobs"

    id: Mapped[uuid.UUID] = uuid_pk()
    customer_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("customers.id"), nullable=False)
    job_name: Mapped[str] = mapped_column(String(255), nullable=False)
    site_address: Mapped[str | None] = mapped_column(Text)
    site_contact: Mapped[str | None] = mapped_column(String(255))
    job_type: Mapped[str | None] = mapped_column(String(120))
    status: Mapped[str] = mapped_column(String(40), default="draft", nullable=False)
    notes: Mapped[str | None] = mapped_column(Text)
    created_at: Mapped[datetime] = created_at_column()
    updated_at: Mapped[datetime] = updated_at_column()

    customer: Mapped[Customer] = relationship(back_populates="jobs")
    attachments: Mapped[list[Attachment]] = relationship(
        back_populates="job", cascade="all, delete-orphan"
    )
    estimates: Mapped[list[Estimate]] = relationship(
        back_populates="job", cascade="all, delete-orphan"
    )


class Attachment(Base):
    __tablename__ = "attachments"

    id: Mapped[uuid.UUID] = uuid_pk()
    job_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("jobs.id"), nullable=False)
    file_name: Mapped[str] = mapped_column(String(255), nullable=False)
    file_type: Mapped[str | None] = mapped_column(String(120))
    storage_key: Mapped[str | None] = mapped_column(String(512))
    storage_url: Mapped[str | None] = mapped_column(String(512))
    uploaded_by: Mapped[str | None] = mapped_column(String(255))
    created_at: Mapped[datetime] = created_at_column()

    job: Mapped[Job] = relationship(back_populates="attachments")


class Material(Base):
    __tablename__ = "materials"

    id: Mapped[uuid.UUID] = uuid_pk()
    sku: Mapped[str] = mapped_column(String(120), unique=True, nullable=False)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    category: Mapped[str | None] = mapped_column(String(120))
    unit: Mapped[str] = mapped_column(String(40), nullable=False)
    unit_cost: Mapped[Decimal] = mapped_column(Money, nullable=False)
    default_markup_percent: Mapped[Decimal] = mapped_column(
        Percent, default=Decimal("0"), nullable=False
    )
    supplier: Mapped[str | None] = mapped_column(String(255))
    manufacturer: Mapped[str | None] = mapped_column(String(255))
    active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    created_at: Mapped[datetime] = created_at_column()
    updated_at: Mapped[datetime] = updated_at_column()

    assembly_materials: Mapped[list[AssemblyMaterial]] = relationship(back_populates="material")


class LaborUnit(Base):
    __tablename__ = "labor_units"

    id: Mapped[uuid.UUID] = uuid_pk()
    code: Mapped[str] = mapped_column(String(120), unique=True, nullable=False)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[str | None] = mapped_column(Text)
    base_hours: Mapped[Decimal] = mapped_column(Numeric(8, 2), nullable=False)
    crew_size: Mapped[Decimal] = mapped_column(Numeric(6, 2), default=Decimal("1"), nullable=False)
    difficulty_factor: Mapped[Decimal] = mapped_column(
        Percent, default=Decimal("1"), nullable=False
    )
    active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    created_at: Mapped[datetime] = created_at_column()
    updated_at: Mapped[datetime] = updated_at_column()

    assembly_labor: Mapped[list[AssemblyLabor]] = relationship(back_populates="labor_unit")


class MarginProfile(Base):
    __tablename__ = "margin_profiles"

    id: Mapped[uuid.UUID] = uuid_pk()
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    material_markup_percent: Mapped[Decimal] = mapped_column(Percent, nullable=False)
    labor_rate_per_hour: Mapped[Decimal] = mapped_column(Money, nullable=False)
    overhead_percent: Mapped[Decimal] = mapped_column(Percent, default=Decimal("0"), nullable=False)
    profit_percent: Mapped[Decimal] = mapped_column(Percent, default=Decimal("0"), nullable=False)
    contingency_percent: Mapped[Decimal] = mapped_column(
        Percent, default=Decimal("0"), nullable=False
    )
    tax_percent: Mapped[Decimal] = mapped_column(Percent, default=Decimal("0"), nullable=False)
    minimum_margin_percent: Mapped[Decimal] = mapped_column(
        Percent, default=Decimal("0"), nullable=False
    )
    active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    created_at: Mapped[datetime] = created_at_column()
    updated_at: Mapped[datetime] = updated_at_column()

    estimates: Mapped[list[Estimate]] = relationship(back_populates="margin_profile")


class Assembly(Base):
    __tablename__ = "assemblies"
    __table_args__ = (UniqueConstraint("code", "version", name="uq_assemblies_code_version"),)

    id: Mapped[uuid.UUID] = uuid_pk()
    code: Mapped[str] = mapped_column(String(120), nullable=False)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    version: Mapped[int] = mapped_column(default=1, nullable=False)
    category: Mapped[str | None] = mapped_column(String(120))
    parameters: Mapped[list[dict]] = mapped_column(JSON, default=list, nullable=False)
    assumptions: Mapped[list[str]] = mapped_column(JSON, default=list, nullable=False)
    exclusions: Mapped[list[str]] = mapped_column(JSON, default=list, nullable=False)
    review_flag_rules: Mapped[list[dict]] = mapped_column(JSON, default=list, nullable=False)
    active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    created_at: Mapped[datetime] = created_at_column()
    updated_at: Mapped[datetime] = updated_at_column()

    materials: Mapped[list[AssemblyMaterial]] = relationship(
        back_populates="assembly", cascade="all, delete-orphan"
    )
    labor: Mapped[list[AssemblyLabor]] = relationship(
        back_populates="assembly", cascade="all, delete-orphan"
    )
    rules: Mapped[list[AssemblyRule]] = relationship(
        back_populates="assembly", cascade="all, delete-orphan"
    )


class AssemblyMaterial(Base):
    __tablename__ = "assembly_materials"

    id: Mapped[uuid.UUID] = uuid_pk()
    assembly_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("assemblies.id"), nullable=False)
    material_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("materials.id"), nullable=False)
    quantity_formula: Mapped[str] = mapped_column(String(255), default="1", nullable=False)
    unit: Mapped[str | None] = mapped_column(String(40))
    notes: Mapped[str | None] = mapped_column(Text)

    assembly: Mapped[Assembly] = relationship(back_populates="materials")
    material: Mapped[Material] = relationship(back_populates="assembly_materials")


class AssemblyLabor(Base):
    __tablename__ = "assembly_labor"

    id: Mapped[uuid.UUID] = uuid_pk()
    assembly_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("assemblies.id"), nullable=False)
    labor_unit_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("labor_units.id"), nullable=False)
    hours_formula: Mapped[str] = mapped_column(String(255), default="base_hours", nullable=False)
    notes: Mapped[str | None] = mapped_column(Text)

    assembly: Mapped[Assembly] = relationship(back_populates="labor")
    labor_unit: Mapped[LaborUnit] = relationship(back_populates="assembly_labor")


class AssemblyRule(Base):
    __tablename__ = "assembly_rules"

    id: Mapped[uuid.UUID] = uuid_pk()
    assembly_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("assemblies.id"), nullable=False)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    rule_json: Mapped[dict] = mapped_column(JSON, nullable=False)
    active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    created_at: Mapped[datetime] = created_at_column()
    updated_at: Mapped[datetime] = updated_at_column()

    assembly: Mapped[Assembly] = relationship(back_populates="rules")


class Estimate(Base):
    __tablename__ = "estimates"

    id: Mapped[uuid.UUID] = uuid_pk()
    job_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("jobs.id"), nullable=False)
    margin_profile_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("margin_profiles.id"), nullable=False
    )
    status: Mapped[str] = mapped_column(String(40), default="draft", nullable=False)
    material_subtotal: Mapped[Decimal] = mapped_column(Money, default=Decimal("0"), nullable=False)
    labor_subtotal: Mapped[Decimal] = mapped_column(Money, default=Decimal("0"), nullable=False)
    equipment_subtotal: Mapped[Decimal] = mapped_column(Money, default=Decimal("0"), nullable=False)
    subcontractor_subtotal: Mapped[Decimal] = mapped_column(
        Money, default=Decimal("0"), nullable=False
    )
    fee_subtotal: Mapped[Decimal] = mapped_column(Money, default=Decimal("0"), nullable=False)
    overhead_total: Mapped[Decimal] = mapped_column(Money, default=Decimal("0"), nullable=False)
    profit_total: Mapped[Decimal] = mapped_column(Money, default=Decimal("0"), nullable=False)
    contingency_total: Mapped[Decimal] = mapped_column(Money, default=Decimal("0"), nullable=False)
    tax_total: Mapped[Decimal] = mapped_column(Money, default=Decimal("0"), nullable=False)
    grand_total: Mapped[Decimal] = mapped_column(Money, default=Decimal("0"), nullable=False)
    snapshot: Mapped[dict] = mapped_column(JSON, default=dict, nullable=False)
    created_at: Mapped[datetime] = created_at_column()
    updated_at: Mapped[datetime] = updated_at_column()

    job: Mapped[Job] = relationship(back_populates="estimates")
    margin_profile: Mapped[MarginProfile] = relationship(back_populates="estimates")
    assemblies: Mapped[list[EstimateAssembly]] = relationship(
        back_populates="estimate", cascade="all, delete-orphan"
    )
    line_items: Mapped[list[EstimateLineItem]] = relationship(
        back_populates="estimate", cascade="all, delete-orphan"
    )
    notes: Mapped[list[EstimateNote]] = relationship(
        back_populates="estimate", cascade="all, delete-orphan"
    )
    review_flags: Mapped[list[EstimateReviewFlag]] = relationship(
        back_populates="estimate", cascade="all, delete-orphan"
    )
    exports: Mapped[list[EstimateExport]] = relationship(
        back_populates="estimate", cascade="all, delete-orphan"
    )


class EstimateAssembly(Base):
    __tablename__ = "estimate_assemblies"

    id: Mapped[uuid.UUID] = uuid_pk()
    estimate_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("estimates.id"), nullable=False)
    assembly_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("assemblies.id"), nullable=False)
    assembly_code: Mapped[str] = mapped_column(String(120), nullable=False)
    assembly_version: Mapped[int] = mapped_column(nullable=False)
    parameters: Mapped[dict] = mapped_column(JSON, default=dict, nullable=False)
    created_at: Mapped[datetime] = created_at_column()
    updated_at: Mapped[datetime] = updated_at_column()

    estimate: Mapped[Estimate] = relationship(back_populates="assemblies")
    assembly: Mapped[Assembly] = relationship()


class EstimateLineItem(Base):
    __tablename__ = "estimate_line_items"

    id: Mapped[uuid.UUID] = uuid_pk()
    estimate_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("estimates.id"), nullable=False)
    source_type: Mapped[str] = mapped_column(String(40), nullable=False)
    source_id: Mapped[uuid.UUID | None] = mapped_column(Uuid(as_uuid=True))
    line_type: Mapped[str] = mapped_column(String(40), nullable=False)
    sku: Mapped[str | None] = mapped_column(String(120))
    description: Mapped[str] = mapped_column(String(255), nullable=False)
    quantity: Mapped[Decimal] = mapped_column(Numeric(12, 3), default=Decimal("1"), nullable=False)
    unit: Mapped[str | None] = mapped_column(String(40))
    unit_cost: Mapped[Decimal] = mapped_column(Money, default=Decimal("0"), nullable=False)
    unit_sell: Mapped[Decimal] = mapped_column(Money, default=Decimal("0"), nullable=False)
    total_cost: Mapped[Decimal] = mapped_column(Money, default=Decimal("0"), nullable=False)
    total_sell: Mapped[Decimal] = mapped_column(Money, default=Decimal("0"), nullable=False)
    labor_hours: Mapped[Decimal | None] = mapped_column(Numeric(8, 2))
    margin_percent: Mapped[Decimal | None] = mapped_column(Percent)
    notes: Mapped[str | None] = mapped_column(Text)
    created_at: Mapped[datetime] = created_at_column()

    estimate: Mapped[Estimate] = relationship(back_populates="line_items")


class EstimateNote(Base):
    __tablename__ = "estimate_notes"

    id: Mapped[uuid.UUID] = uuid_pk()
    estimate_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("estimates.id"), nullable=False)
    note_type: Mapped[str] = mapped_column(String(40), nullable=False)
    note: Mapped[str] = mapped_column(Text, nullable=False)
    source_type: Mapped[str | None] = mapped_column(String(40))
    source_id: Mapped[uuid.UUID | None] = mapped_column(Uuid(as_uuid=True))
    created_at: Mapped[datetime] = created_at_column()

    estimate: Mapped[Estimate] = relationship(back_populates="notes")


class EstimateReviewFlag(Base):
    __tablename__ = "estimate_review_flags"

    id: Mapped[uuid.UUID] = uuid_pk()
    estimate_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("estimates.id"), nullable=False)
    flag_code: Mapped[str] = mapped_column(String(120), nullable=False)
    severity: Mapped[str] = mapped_column(String(40), nullable=False)
    message: Mapped[str] = mapped_column(Text, nullable=False)
    source_type: Mapped[str | None] = mapped_column(String(40))
    source_id: Mapped[uuid.UUID | None] = mapped_column(Uuid(as_uuid=True))
    created_at: Mapped[datetime] = created_at_column()

    estimate: Mapped[Estimate] = relationship(back_populates="review_flags")


class EstimateExport(Base):
    __tablename__ = "estimate_exports"

    id: Mapped[uuid.UUID] = uuid_pk()
    estimate_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("estimates.id"), nullable=False)
    export_type: Mapped[str] = mapped_column(String(40), nullable=False)
    file_name: Mapped[str] = mapped_column(String(255), nullable=False)
    storage_key: Mapped[str | None] = mapped_column(String(512))
    created_at: Mapped[datetime] = created_at_column()

    estimate: Mapped[Estimate] = relationship(back_populates="exports")
