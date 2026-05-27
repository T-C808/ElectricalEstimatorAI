# Electrical Estimator + BOM Engine

V1 estimating and bill-of-materials app for small electrical contractors. It focuses on the estimating wedge only: customers, jobs, editable catalogs, versioned assemblies, deterministic rules, estimate snapshots, assumptions, exclusions, review flags, and supplier/internal/client exports.

## Local URLs

```text
Frontend: http://localhost:5173
API:      http://localhost:8000
API Docs: http://localhost:8000/docs
Postgres: localhost:5432
```

## Setup

```bash
cp .env.example .env
make install
docker compose up -d db
make migrate
make seed
make dev
```

`make dev` starts Postgres, the FastAPI API, and the Vite frontend through Docker Compose.

## Commands

```bash
make dev      # start local services
make test     # backend pytest + frontend vitest
make lint     # backend ruff + frontend eslint
make format   # backend ruff format + frontend prettier
make migrate  # apply Alembic migrations
make seed     # load default margin profile, materials, labor, and assemblies
```

## Critical V1 Flow

1. Seed data.
2. Create a customer.
3. Create a job.
4. Create an estimate for the job with the default margin profile.
5. Add `ATS-600-BYPASS` and a feeder assembly such as `FEEDER-EMT`.
6. Enter feeder length, conduit type, service size, and review parameters.
7. Calculate the estimate.
8. Review line items, totals, assumptions, exclusions, and review flags.
9. Export supplier BOM CSV, internal BOM CSV, and client PDF.

## Required Disclaimer

Every estimate review and client PDF includes:

```text
This estimate is based on the information provided and listed assumptions. Final installation is subject to field verification, applicable code requirements, utility requirements, and AHJ approval. This estimate is not a substitute for code compliance review or AHJ approval.
```

## V1 Boundaries

Included: estimating, material/labor catalog, margin profiles, assemblies, rules, estimate snapshots, CSV/PDF exports, assumptions, exclusions, review flags.

Excluded: scheduling, dispatching, technician routing, payments, inventory tracking, accounting integrations, customer portal, permit automation, and full code-compliance validation.
