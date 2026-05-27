# AGENTS.md

This file provides repository-level instructions for Codex and other coding agents.

## Project

Electrical Estimating + BOM Engine for small electrical contractors.

The application should behave like a junior estimator: it turns job inputs, catalog pricing, reusable assemblies, and controlled rules into a priced estimate, bill of materials, assumptions, exclusions, and review flags.

## Product Boundaries

Build the estimating/BOM wedge first.

In scope for V1:

- customers,
- jobs,
- attachments metadata,
- material catalog,
- labor catalog,
- margin profiles,
- versioned assemblies,
- controlled rules engine,
- estimate generation,
- estimate snapshots,
- supplier CSV export,
- internal CSV export,
- client PDF export,
- assumptions, exclusions, and review flags.

Out of scope for V1:

- scheduling,
- dispatching,
- technician mobile app,
- payments,
- accounting integrations,
- inventory tracking,
- customer portal,
- permit automation,
- full NEC/code validation,
- AI-generated final pricing without human review.

## Required Engineering Approach

1. Preserve pricing trust over UI polish.
2. Version or snapshot anything that can affect an estimate.
3. Make estimate line items traceable to manual entry, assembly, or rule.
4. Use deterministic rules and tests for pricing logic.
5. Avoid raw `eval`, arbitrary code execution, or SQL expressions in formulas.
6. Keep human review in the loop.
7. Every client-facing estimate must include assumptions, exclusions, and code/AHJ disclaimer.

## Preferred Stack

Backend:

- Python
- FastAPI
- Pydantic
- SQLAlchemy 2.x
- Alembic
- Postgres
- pytest

Frontend:

- React
- TypeScript
- Vite
- Tailwind
- TanStack Query
- React Hook Form
- Zod

Local development:

- Docker Compose
- Makefile commands

## Expected Commands

Create these commands if they do not exist:

```bash
make dev
make test
make lint
make format
make migrate
make seed
```

`make dev` should start the database, API, and frontend locally.

## Backend Conventions

Use this module layout when starting from scratch:

```text
apps/api/app/
├── main.py
├── api/
├── core/
├── db/
├── domain/
├── exports/
├── models/
├── schemas/
└── services/
```

Guidelines:

- Put business logic in services or domain modules, not route handlers.
- Keep route handlers thin.
- Use Pydantic schemas for request/response contracts.
- Use SQLAlchemy models for persistence.
- Add database constraints for uniqueness and required fields.
- Use Decimal for money math where practical.
- Avoid floats for persisted money values.
- Return useful validation errors.

## Frontend Conventions

Use feature-oriented folders:

```text
apps/web/src/
├── app/
├── components/
├── features/
├── lib/
└── routes/
```

Guidelines:

- Use React Hook Form and Zod for forms.
- Use TanStack Query for server state.
- Keep presentational components simple.
- Show calculation traceability in the estimate builder.
- Highlight review flags and missing required inputs.
- Do not hide assumptions and exclusions.

## Pricing Rules

Use the V1 pricing formula:

```text
material_sell = material_cost * (1 + material_markup_percent)
labor_sell = labor_hours * labor_rate_per_hour
subtotal = material_sell + labor_sell + equipment_sell + subcontractor_sell + fee_sell
overhead = subtotal * overhead_percent
profit = (subtotal + overhead) * profit_percent
contingency = (subtotal + overhead + profit) * contingency_percent
tax = taxable_amount * tax_percent
total = subtotal + overhead + profit + contingency + tax
```

Keep tax simple and configurable. If tax implementation is incomplete, default it to zero and make that explicit in the UI.

## Required Estimate Disclaimer

Include this exact disclaimer in client PDF output and estimate review screens:

```text
This estimate is based on the information provided and listed assumptions. Final installation is subject to field verification, applicable code requirements, utility requirements, and AHJ approval. This estimate is not a substitute for code compliance review or AHJ approval.
```

## Review Flags

Generate review flags for:

- service size >= 400A,
- ATS included,
- generator interconnection included,
- NETA testing selected,
- shutdown required,
- utility coordination required,
- unknown existing equipment,
- missing feeder length,
- missing conduit type,
- manual override used,
- margin below minimum threshold.

## Testing Expectations

Minimum backend tests:

- price calculation totals,
- material markup behavior,
- labor rate behavior,
- overhead/profit/contingency behavior,
- rule conditions,
- formula evaluation whitelist,
- assembly estimate generation,
- estimate snapshot immutability,
- CSV export shape.

Minimum frontend tests:

- estimate builder renders selected assemblies,
- required parameter validation,
- calculation result display,
- review flags display.

## Commit/PR Behavior

When Codex completes a task, summarize:

- files changed,
- features implemented,
- tests added,
- commands run,
- known gaps.

Do not claim tests passed unless they were actually run.
