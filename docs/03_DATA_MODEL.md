# Data Model

## Tables

Recommended core tables:

```text
customers
jobs
attachments
materials
labor_units
margin_profiles
assemblies
assembly_materials
assembly_labor
assembly_rules
estimates
estimate_assemblies
estimate_line_items
estimate_notes
estimate_review_flags
estimate_exports
```

JSONB can be used for assembly parameters and rules in V1, but core estimate line items should be relational for queryability and export simplicity.

## Customers

```text
id uuid primary key
company_name text
contact_name text
email text
phone text
billing_address text
notes text
created_at timestamp
updated_at timestamp
```

## Jobs

```text
id uuid primary key
customer_id uuid references customers(id)
job_name text not null
site_address text
site_contact text
job_type text
status text not null default 'draft'
notes text
created_at timestamp
updated_at timestamp
```

Allowed statuses:

```text
draft
estimating
review_required
approved
sent
won
lost
archived
```

## Attachments

```text
id uuid primary key
job_id uuid references jobs(id)
file_name text not null
file_type text
storage_key text
storage_url text
uploaded_by text
created_at timestamp
```

For local V1, store metadata and optionally save files to a local `storage/` directory.

## Materials

```text
id uuid primary key
sku text unique not null
name text not null
category text
unit text not null
unit_cost numeric(12,2) not null
default_markup_percent numeric(8,4) not null default 0
supplier text
manufacturer text
active boolean not null default true
created_at timestamp
updated_at timestamp
```

## Labor Units

```text
id uuid primary key
code text unique not null
name text not null
description text
base_hours numeric(8,2) not null
crew_size numeric(6,2) default 1
difficulty_factor numeric(8,4) default 1
active boolean not null default true
created_at timestamp
updated_at timestamp
```

## Margin Profiles

```text
id uuid primary key
name text not null
material_markup_percent numeric(8,4) not null
labor_rate_per_hour numeric(12,2) not null
overhead_percent numeric(8,4) not null default 0
profit_percent numeric(8,4) not null default 0
contingency_percent numeric(8,4) not null default 0
tax_percent numeric(8,4) not null default 0
minimum_margin_percent numeric(8,4) not null default 0
active boolean not null default true
created_at timestamp
updated_at timestamp
```

## Assemblies

```text
id uuid primary key
code text not null
name text not null
version integer not null default 1
category text
parameters jsonb not null default '[]'
assumptions jsonb not null default '[]'
exclusions jsonb not null default '[]'
review_flag_rules jsonb not null default '[]'
active boolean not null default true
created_at timestamp
updated_at timestamp
unique(code, version)
```

## Assembly Materials

```text
id uuid primary key
assembly_id uuid references assemblies(id)
material_id uuid references materials(id)
quantity_formula text not null default '1'
unit text
notes text
```

Use `quantity_formula` even for fixed quantities so feeder-length-based items can be handled consistently.

## Assembly Labor

```text
id uuid primary key
assembly_id uuid references assemblies(id)
labor_unit_id uuid references labor_units(id)
hours_formula text not null default 'base_hours'
notes text
```

## Assembly Rules

```text
id uuid primary key
assembly_id uuid references assemblies(id)
name text not null
rule_json jsonb not null
active boolean not null default true
created_at timestamp
updated_at timestamp
```

## Estimates

```text
id uuid primary key
job_id uuid references jobs(id)
margin_profile_id uuid references margin_profiles(id)
status text not null default 'draft'
material_subtotal numeric(12,2) not null default 0
labor_subtotal numeric(12,2) not null default 0
equipment_subtotal numeric(12,2) not null default 0
subcontractor_subtotal numeric(12,2) not null default 0
fee_subtotal numeric(12,2) not null default 0
overhead_total numeric(12,2) not null default 0
profit_total numeric(12,2) not null default 0
contingency_total numeric(12,2) not null default 0
tax_total numeric(12,2) not null default 0
grand_total numeric(12,2) not null default 0
snapshot jsonb not null default '{}'
created_at timestamp
updated_at timestamp
```

## Estimate Assemblies

```text
id uuid primary key
estimate_id uuid references estimates(id)
assembly_id uuid references assemblies(id)
assembly_code text not null
assembly_version integer not null
parameters jsonb not null default '{}'
created_at timestamp
updated_at timestamp
```

## Estimate Line Items

```text
id uuid primary key
estimate_id uuid references estimates(id)
source_type text not null
source_id uuid
line_type text not null
sku text
description text not null
quantity numeric(12,3) not null default 1
unit text
unit_cost numeric(12,2) not null default 0
unit_sell numeric(12,2) not null default 0
total_cost numeric(12,2) not null default 0
total_sell numeric(12,2) not null default 0
labor_hours numeric(8,2)
margin_percent numeric(8,4)
notes text
created_at timestamp
```

Allowed `source_type`:

```text
manual
assembly
rule
```

Allowed `line_type`:

```text
material
labor
equipment
subcontractor
fee
note
```

## Estimate Notes

```text
id uuid primary key
estimate_id uuid references estimates(id)
note_type text not null
note text not null
source_type text
source_id uuid
created_at timestamp
```

Allowed note types:

```text
assumption
exclusion
internal_note
client_note
disclaimer
```

## Estimate Review Flags

```text
id uuid primary key
estimate_id uuid references estimates(id)
flag_code text not null
severity text not null
message text not null
source_type text
source_id uuid
created_at timestamp
```

Allowed severities:

```text
info
warning
critical
```

## Estimate Exports

```text
id uuid primary key
estimate_id uuid references estimates(id)
export_type text not null
file_name text not null
storage_key text
created_at timestamp
```

Allowed export types:

```text
supplier_csv
internal_csv
client_pdf
```
