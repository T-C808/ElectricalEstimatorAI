# Tasks for Codex

Use this as the execution checklist.

## Task 1: Scaffold Local Dev

- Create monorepo layout.
- Add Docker Compose with Postgres.
- Add FastAPI app.
- Add React/Vite app.
- Add Makefile.
- Add README setup instructions.

Acceptance:

- `make dev` starts app services.
- API health endpoint works.
- Frontend loads.

## Task 2: Database Models and Migrations

- Implement models from `docs/03_DATA_MODEL.md`.
- Add Alembic.
- Create initial migration.

Acceptance:

- `make migrate` succeeds.
- Database tables are created.

## Task 3: Seed Data

- Implement seed command.
- Seed default margin profile.
- Seed starter materials.
- Seed starter labor units.
- Seed starter assemblies.

Acceptance:

- `make seed` succeeds.
- API can list seed records.

## Task 4: CRUD APIs

- Customers.
- Jobs.
- Materials.
- Labor units.
- Margin profiles.
- Assemblies.

Acceptance:

- API routes work through Swagger/OpenAPI.
- Validation errors are useful.

## Task 5: Estimate Engine

- Create estimate.
- Add assembly to estimate.
- Store parameters.
- Expand base materials/labor.
- Calculate totals.
- Store line items.
- Store snapshot.

Acceptance:

- Estimate can be calculated from `ATS-600-BYPASS`.
- Totals are persisted.

## Task 6: Rules Engine

- Add safe formula evaluator.
- Add conditions.
- Add actions.
- Add rule tests.

Acceptance:

- Feeder length drives material quantities.
- Rigid conduit increases labor.
- Shutdown adds labor and review flag.
- NETA adds support and exclusion.
- Unsafe formulas are rejected.

## Task 7: Exports

- Supplier CSV.
- Internal CSV.
- Client PDF.

Acceptance:

- Supplier CSV excludes internal pricing.
- Internal CSV includes cost/sell details.
- Client PDF includes disclaimer.

## Task 8: Frontend

- Dashboard.
- Customer pages.
- Job pages.
- Catalog pages.
- Assembly library.
- Estimate builder.
- Export panel.

Acceptance:

- A user can complete the critical V1 flow in the browser.

## Task 9: Tests and Cleanup

- Add backend tests.
- Add frontend smoke tests where practical.
- Run lint/format/test.
- Update README with exact commands.

Acceptance:

- Commands run successfully or known failures are documented.
