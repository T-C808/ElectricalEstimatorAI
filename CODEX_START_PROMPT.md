# Codex Start Prompt: Electrical Estimating + BOM Engine

You are Codex acting as a senior full-stack engineer. Build a production-minded V1 MVP for a simple estimating and bill-of-materials engine for small electrical contractors.

## Core Product Goal

Build a catalog-driven estimating application that lets an owner-led electrical shop create jobs, select reusable estimating assemblies, adjust parameters such as feeder length and conduit type, and generate:

- a priced estimate,
- a supplier-ready BOM CSV,
- an internal BOM CSV,
- a client/internal PDF,
- assumptions,
- exclusions,
- review flags.

This is not a field-service platform. Do not build scheduling, dispatching, payments, technician routing, customer portal, inventory management, or accounting integrations in V1.

## Required Stack

Use this stack unless the existing repository already proves otherwise:

- Frontend: React, TypeScript, Vite, Tailwind, TanStack Query, React Hook Form, Zod.
- Backend: Python, FastAPI, Pydantic, SQLAlchemy 2.x, Alembic.
- Database: Postgres.
- Local dev: Docker Compose.
- Tests: pytest for backend, Vitest or React Testing Library for frontend.
- Export generation: CSV from standard Python libraries; PDF with a stable Python library such as WeasyPrint or ReportLab.

## First Actions

1. Inspect the repository.
2. Read `AGENTS.md`.
3. Read all files under `docs/`.
4. If the repository is empty or mostly empty, scaffold a monorepo.
5. If code already exists, preserve the current structure and adapt these requirements to it.

## Target Repository Shape

If starting from scratch, create:

```text
.
├── AGENTS.md
├── README.md
├── docker-compose.yml
├── Makefile
├── apps
│   ├── api
│   │   ├── pyproject.toml
│   │   ├── alembic.ini
│   │   ├── alembic/
│   │   ├── app/
│   │   │   ├── main.py
│   │   │   ├── api/
│   │   │   ├── core/
│   │   │   ├── db/
│   │   │   ├── domain/
│   │   │   ├── models/
│   │   │   ├── schemas/
│   │   │   ├── services/
│   │   │   └── exports/
│   │   └── tests/
│   └── web
│       ├── package.json
│       ├── vite.config.ts
│       ├── tailwind.config.ts
│       ├── src/
│       │   ├── app/
│       │   ├── components/
│       │   ├── features/
│       │   ├── lib/
│       │   └── routes/
│       └── tests/
└── docs/
```

## V1 Features to Implement

### 1. Customer and Job Records

Implement CRUD for customers and jobs.

Customer fields:

```text
id
company_name
contact_name
email
phone
billing_address
notes
created_at
updated_at
```

Job fields:

```text
id
customer_id
job_name
site_address
site_contact
job_type
status
notes
created_at
updated_at
```

Allowed job statuses:

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

Attachments can be modeled in the database, but actual object storage integration can be stubbed for local V1.

### 2. Pricing Catalog

Implement CRUD for:

- materials,
- labor units,
- margin profiles.

Material fields:

```text
id
sku
name
category
unit
unit_cost
default_markup_percent
supplier
manufacturer
active
created_at
updated_at
```

Labor unit fields:

```text
id
code
name
description
base_hours
crew_size
difficulty_factor
active
created_at
updated_at
```

Margin profile fields:

```text
id
name
material_markup_percent
labor_rate_per_hour
overhead_percent
profit_percent
contingency_percent
tax_percent
active
created_at
updated_at
```

### 3. Assembly-Based Estimating

Implement reusable assemblies with:

- versioned assembly code,
- display name,
- category,
- parameter definitions,
- base materials,
- base labor,
- rules,
- assumptions,
- exclusions,
- review flag rules.

Required starter assemblies:

- `ATS-600-BYPASS`: 600A ATS install with bypass.
- `ATS-400`: 400A ATS install.
- `PANEL-NEMA-3R`: NEMA 3R panel upgrade.
- `PANEL-NEMA-3RX`: NEMA 3RX panel upgrade.
- `FEEDER-EMT`: Feeder run in EMT.
- `FEEDER-PVC`: Feeder run in PVC.
- `FEEDER-RIGID`: Feeder run in rigid conduit.
- `SHUTDOWN-COORD`: Shutdown coordination allowance.
- `NETA-SUPPORT`: NETA testing support allowance.
- `GROUNDING-BONDING`: Grounding/bonding allowance.

### 4. Rules Engine

Implement a deterministic, test-covered rules engine. Do not use raw `eval`, JavaScript execution, SQL expressions, or arbitrary Python execution.

Supported conditions:

- equals,
- not_equals,
- greater_than,
- greater_than_or_equal,
- less_than,
- less_than_or_equal,
- in,
- exists.

Supported actions:

- add_material,
- add_labor,
- multiply_labor,
- add_note,
- add_exclusion,
- add_assumption,
- require_review.

Use a whitelisted formula evaluator for quantity formulas. Allowed variables for V1:

```text
feeder_length_ft
conductor_count
conduit_count
waste_factor
crew_size
difficulty_factor
```

Allowed operators:

```text
+ - * / ( )
```

### 5. Estimate Generation

Implement estimate generation from selected assemblies and parameters.

Each estimate must snapshot:

- material costs,
- labor rates,
- margin profile values,
- assembly versions,
- rule versions or rule JSON,
- generated line items,
- notes,
- assumptions,
- exclusions,
- review flags.

Do not let future catalog updates mutate existing estimates.

Estimate statuses:

```text
draft
calculated
review_required
approved
sent
won
lost
archived
```

Line item source types:

```text
manual
assembly
rule
```

Line item types:

```text
material
labor
equipment
subcontractor
fee
note
```

### 6. Exports

Implement:

- supplier BOM CSV,
- internal BOM CSV,
- client PDF.

Supplier CSV must not include internal markup, labor pricing, profit, overhead, or margin.

Client PDF must include this disclaimer:

```text
This estimate is based on the information provided and listed assumptions. Final installation is subject to field verification, applicable code requirements, utility requirements, and AHJ approval. This estimate is not a substitute for code compliance review or AHJ approval.
```

### 7. Guardrails

Every generated estimate must include:

- assumptions,
- exclusions,
- human review requirement before customer submission,
- code/AHJ disclaimer,
- review flags when triggered.

Trigger review when any of the following are true:

- service size is 400A or greater,
- ATS is included,
- generator interconnection is included,
- NETA testing is selected,
- shutdown is required,
- utility coordination is required,
- existing equipment is unknown,
- feeder length is missing,
- conduit type is missing,
- manual override is used,
- margin is below configured minimum.

## API Requirements

Implement REST endpoints described in `docs/04_API_SPEC.md`.

API responses should be predictable and typed. Use Pydantic schemas. Return useful validation errors.

## UI Requirements

Build a functional owner/admin workflow:

1. Dashboard listing recent jobs and estimates.
2. Customer create/edit/list/detail.
3. Job create/edit/detail.
4. Catalog pages for materials, labor, and margins.
5. Assembly library page.
6. Estimate builder:
   - select job,
   - choose margin profile,
   - add assemblies,
   - configure parameters,
   - calculate estimate,
   - view line items,
   - view assumptions/exclusions/review flags,
   - export CSV/PDF.

Keep the UI clean and utilitarian. Optimize for trust, traceability, and speed.

## Implementation Milestones

Implement in this order:

1. Repo scaffold and local dev environment.
2. Database models and migrations.
3. Seed data for materials, labor units, margin profile, and starter assemblies.
4. Customer/job/catalog CRUD API.
5. Estimate calculation domain service.
6. Rules engine with unit tests.
7. Export services.
8. Frontend pages and forms.
9. End-to-end vertical smoke test.
10. README with setup and usage instructions.

## Definition of Done

V1 is done when a developer can run:

```bash
make dev
```

Then open the web app, create or use seed data, create a job, select `ATS-600-BYPASS`, enter feeder length and conduit type, calculate an estimate, inspect line items, see assumptions/exclusions/review flags, and export supplier CSV, internal CSV, and client PDF.

## Constraints

- Prefer simple, explicit code over clever abstractions.
- Add tests for pricing math and rule evaluation.
- Do not implement payments, dispatching, scheduling, accounting, or inventory tracking.
- Do not perform code compliance validation. Only include disclaimers and review flags.
- Do not store secrets in code.
- Do not require external paid services for local development.
