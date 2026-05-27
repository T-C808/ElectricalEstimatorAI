from __future__ import annotations

from alembic import op
import sqlalchemy as sa

revision = "0001_initial"
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "customers",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("company_name", sa.String(length=255), nullable=True),
        sa.Column("contact_name", sa.String(length=255), nullable=True),
        sa.Column("email", sa.String(length=255), nullable=True),
        sa.Column("phone", sa.String(length=80), nullable=True),
        sa.Column("billing_address", sa.Text(), nullable=True),
        sa.Column("notes", sa.Text(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_table(
        "materials",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("sku", sa.String(length=120), nullable=False),
        sa.Column("name", sa.String(length=255), nullable=False),
        sa.Column("category", sa.String(length=120), nullable=True),
        sa.Column("unit", sa.String(length=40), nullable=False),
        sa.Column("unit_cost", sa.Numeric(12, 2), nullable=False),
        sa.Column("default_markup_percent", sa.Numeric(8, 4), nullable=False),
        sa.Column("supplier", sa.String(length=255), nullable=True),
        sa.Column("manufacturer", sa.String(length=255), nullable=True),
        sa.Column("active", sa.Boolean(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("sku"),
    )
    op.create_table(
        "labor_units",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("code", sa.String(length=120), nullable=False),
        sa.Column("name", sa.String(length=255), nullable=False),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column("base_hours", sa.Numeric(8, 2), nullable=False),
        sa.Column("crew_size", sa.Numeric(6, 2), nullable=False),
        sa.Column("difficulty_factor", sa.Numeric(8, 4), nullable=False),
        sa.Column("active", sa.Boolean(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("code"),
    )
    op.create_table(
        "margin_profiles",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("name", sa.String(length=255), nullable=False),
        sa.Column("material_markup_percent", sa.Numeric(8, 4), nullable=False),
        sa.Column("labor_rate_per_hour", sa.Numeric(12, 2), nullable=False),
        sa.Column("overhead_percent", sa.Numeric(8, 4), nullable=False),
        sa.Column("profit_percent", sa.Numeric(8, 4), nullable=False),
        sa.Column("contingency_percent", sa.Numeric(8, 4), nullable=False),
        sa.Column("tax_percent", sa.Numeric(8, 4), nullable=False),
        sa.Column("minimum_margin_percent", sa.Numeric(8, 4), nullable=False),
        sa.Column("active", sa.Boolean(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_table(
        "jobs",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("customer_id", sa.Uuid(), nullable=False),
        sa.Column("job_name", sa.String(length=255), nullable=False),
        sa.Column("site_address", sa.Text(), nullable=True),
        sa.Column("site_contact", sa.String(length=255), nullable=True),
        sa.Column("job_type", sa.String(length=120), nullable=True),
        sa.Column("status", sa.String(length=40), nullable=False),
        sa.Column("notes", sa.Text(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.ForeignKeyConstraint(["customer_id"], ["customers.id"]),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_table(
        "assemblies",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("code", sa.String(length=120), nullable=False),
        sa.Column("name", sa.String(length=255), nullable=False),
        sa.Column("version", sa.Integer(), nullable=False),
        sa.Column("category", sa.String(length=120), nullable=True),
        sa.Column("parameters", sa.JSON(), nullable=False),
        sa.Column("assumptions", sa.JSON(), nullable=False),
        sa.Column("exclusions", sa.JSON(), nullable=False),
        sa.Column("review_flag_rules", sa.JSON(), nullable=False),
        sa.Column("active", sa.Boolean(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("code", "version", name="uq_assemblies_code_version"),
    )
    op.create_table(
        "attachments",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("job_id", sa.Uuid(), nullable=False),
        sa.Column("file_name", sa.String(length=255), nullable=False),
        sa.Column("file_type", sa.String(length=120), nullable=True),
        sa.Column("storage_key", sa.String(length=512), nullable=True),
        sa.Column("storage_url", sa.String(length=512), nullable=True),
        sa.Column("uploaded_by", sa.String(length=255), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.ForeignKeyConstraint(["job_id"], ["jobs.id"]),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_table(
        "assembly_materials",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("assembly_id", sa.Uuid(), nullable=False),
        sa.Column("material_id", sa.Uuid(), nullable=False),
        sa.Column("quantity_formula", sa.String(length=255), nullable=False),
        sa.Column("unit", sa.String(length=40), nullable=True),
        sa.Column("notes", sa.Text(), nullable=True),
        sa.ForeignKeyConstraint(["assembly_id"], ["assemblies.id"]),
        sa.ForeignKeyConstraint(["material_id"], ["materials.id"]),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_table(
        "assembly_labor",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("assembly_id", sa.Uuid(), nullable=False),
        sa.Column("labor_unit_id", sa.Uuid(), nullable=False),
        sa.Column("hours_formula", sa.String(length=255), nullable=False),
        sa.Column("notes", sa.Text(), nullable=True),
        sa.ForeignKeyConstraint(["assembly_id"], ["assemblies.id"]),
        sa.ForeignKeyConstraint(["labor_unit_id"], ["labor_units.id"]),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_table(
        "assembly_rules",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("assembly_id", sa.Uuid(), nullable=False),
        sa.Column("name", sa.String(length=255), nullable=False),
        sa.Column("rule_json", sa.JSON(), nullable=False),
        sa.Column("active", sa.Boolean(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.ForeignKeyConstraint(["assembly_id"], ["assemblies.id"]),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_table(
        "estimates",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("job_id", sa.Uuid(), nullable=False),
        sa.Column("margin_profile_id", sa.Uuid(), nullable=False),
        sa.Column("status", sa.String(length=40), nullable=False),
        sa.Column("material_subtotal", sa.Numeric(12, 2), nullable=False),
        sa.Column("labor_subtotal", sa.Numeric(12, 2), nullable=False),
        sa.Column("equipment_subtotal", sa.Numeric(12, 2), nullable=False),
        sa.Column("subcontractor_subtotal", sa.Numeric(12, 2), nullable=False),
        sa.Column("fee_subtotal", sa.Numeric(12, 2), nullable=False),
        sa.Column("overhead_total", sa.Numeric(12, 2), nullable=False),
        sa.Column("profit_total", sa.Numeric(12, 2), nullable=False),
        sa.Column("contingency_total", sa.Numeric(12, 2), nullable=False),
        sa.Column("tax_total", sa.Numeric(12, 2), nullable=False),
        sa.Column("grand_total", sa.Numeric(12, 2), nullable=False),
        sa.Column("snapshot", sa.JSON(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.ForeignKeyConstraint(["job_id"], ["jobs.id"]),
        sa.ForeignKeyConstraint(["margin_profile_id"], ["margin_profiles.id"]),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_table(
        "estimate_assemblies",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("estimate_id", sa.Uuid(), nullable=False),
        sa.Column("assembly_id", sa.Uuid(), nullable=False),
        sa.Column("assembly_code", sa.String(length=120), nullable=False),
        sa.Column("assembly_version", sa.Integer(), nullable=False),
        sa.Column("parameters", sa.JSON(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.ForeignKeyConstraint(["assembly_id"], ["assemblies.id"]),
        sa.ForeignKeyConstraint(["estimate_id"], ["estimates.id"]),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_table(
        "estimate_line_items",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("estimate_id", sa.Uuid(), nullable=False),
        sa.Column("source_type", sa.String(length=40), nullable=False),
        sa.Column("source_id", sa.Uuid(), nullable=True),
        sa.Column("line_type", sa.String(length=40), nullable=False),
        sa.Column("sku", sa.String(length=120), nullable=True),
        sa.Column("description", sa.String(length=255), nullable=False),
        sa.Column("quantity", sa.Numeric(12, 3), nullable=False),
        sa.Column("unit", sa.String(length=40), nullable=True),
        sa.Column("unit_cost", sa.Numeric(12, 2), nullable=False),
        sa.Column("unit_sell", sa.Numeric(12, 2), nullable=False),
        sa.Column("total_cost", sa.Numeric(12, 2), nullable=False),
        sa.Column("total_sell", sa.Numeric(12, 2), nullable=False),
        sa.Column("labor_hours", sa.Numeric(8, 2), nullable=True),
        sa.Column("margin_percent", sa.Numeric(8, 4), nullable=True),
        sa.Column("notes", sa.Text(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.ForeignKeyConstraint(["estimate_id"], ["estimates.id"]),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_table(
        "estimate_notes",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("estimate_id", sa.Uuid(), nullable=False),
        sa.Column("note_type", sa.String(length=40), nullable=False),
        sa.Column("note", sa.Text(), nullable=False),
        sa.Column("source_type", sa.String(length=40), nullable=True),
        sa.Column("source_id", sa.Uuid(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.ForeignKeyConstraint(["estimate_id"], ["estimates.id"]),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_table(
        "estimate_review_flags",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("estimate_id", sa.Uuid(), nullable=False),
        sa.Column("flag_code", sa.String(length=120), nullable=False),
        sa.Column("severity", sa.String(length=40), nullable=False),
        sa.Column("message", sa.Text(), nullable=False),
        sa.Column("source_type", sa.String(length=40), nullable=True),
        sa.Column("source_id", sa.Uuid(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.ForeignKeyConstraint(["estimate_id"], ["estimates.id"]),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_table(
        "estimate_exports",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("estimate_id", sa.Uuid(), nullable=False),
        sa.Column("export_type", sa.String(length=40), nullable=False),
        sa.Column("file_name", sa.String(length=255), nullable=False),
        sa.Column("storage_key", sa.String(length=512), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.ForeignKeyConstraint(["estimate_id"], ["estimates.id"]),
        sa.PrimaryKeyConstraint("id"),
    )


def downgrade() -> None:
    op.drop_table("estimate_exports")
    op.drop_table("estimate_review_flags")
    op.drop_table("estimate_notes")
    op.drop_table("estimate_line_items")
    op.drop_table("estimate_assemblies")
    op.drop_table("estimates")
    op.drop_table("assembly_rules")
    op.drop_table("assembly_labor")
    op.drop_table("assembly_materials")
    op.drop_table("attachments")
    op.drop_table("assemblies")
    op.drop_table("jobs")
    op.drop_table("margin_profiles")
    op.drop_table("labor_units")
    op.drop_table("materials")
    op.drop_table("customers")
