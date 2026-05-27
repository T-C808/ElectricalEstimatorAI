# Delivery Plan

## Milestone 0: Repo Setup

Deliverables:

- Monorepo structure.
- Docker Compose with Postgres.
- FastAPI app boots.
- Vite React app boots.
- Makefile with common commands.
- README setup instructions.

Definition of done:

```bash
make dev
```

starts local services.

## Milestone 1: Database and Seed Data

Deliverables:

- SQLAlchemy models.
- Alembic migrations.
- Seed command.
- Materials seed.
- Labor units seed.
- Margin profile seed.
- Starter assemblies seed.

Definition of done:

- `make migrate` applies migrations.
- `make seed` loads starter catalog.
- API can list seeded data.

## Milestone 2: Customer, Job, Catalog CRUD

Deliverables:

- Customer CRUD API and UI.
- Job CRUD API and UI.
- Material CRUD API and UI.
- Labor unit CRUD API and UI.
- Margin profile CRUD API and UI.

Definition of done:

- User can create customer/job.
- User can edit catalog values.

## Milestone 3: Assembly Library

Deliverables:

- Assembly API.
- Assembly detail UI.
- Parameter schema rendering.
- Base materials/labor display.

Definition of done:

- User can browse starter assemblies and see their pricing components.

## Milestone 4: Estimate Domain Engine

Deliverables:

- Add assembly to estimate.
- Store assembly parameters.
- Expand base materials and labor.
- Apply pricing formula.
- Store line items.
- Store snapshot.

Definition of done:

- User can calculate an estimate with at least one assembly.

## Milestone 5: Rules Engine

Deliverables:

- Safe formula evaluator.
- Rule condition evaluator.
- Rule action executor.
- Rule-generated line items and notes.
- Review flag generator.
- Unit tests.

Definition of done:

- Feeder length changes quantity.
- Rigid conduit increases labor.
- Shutdown adds review flag.
- NETA adds review flag and exclusion.

## Milestone 6: Exports

Deliverables:

- Supplier BOM CSV.
- Internal BOM CSV.
- Client PDF.
- Export metadata.
- Download endpoints.
- Export buttons in UI.

Definition of done:

- User can generate and download all three export types.

## Milestone 7: UI Polish and Smoke Test

Deliverables:

- Dashboard.
- Estimate review screen.
- Better errors and loading states.
- End-to-end smoke test instructions.

Definition of done:

A user can complete this flow:

```text
Create customer -> Create job -> Create estimate -> Add ATS-600-BYPASS -> Enter feeder length/conduit -> Calculate -> Review flags -> Export files
```

## Suggested Task Order for Codex

1. Scaffold backend and frontend.
2. Add database models/migrations.
3. Add seed data.
4. Add API routes.
5. Add backend tests for domain logic.
6. Add frontend routes.
7. Wire estimate builder.
8. Add exports.
9. Run tests and fix failures.
10. Update README.
