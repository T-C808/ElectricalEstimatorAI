# Architecture

## Overview

Use a simple web app architecture:

```text
React/Vite frontend -> FastAPI backend -> Postgres
                          |
                          -> CSV/PDF export service
                          -> local/object storage abstraction for attachments and exports
```

## Backend Layers

### API Layer

FastAPI route handlers. Keep them thin.

Responsibilities:

- request validation,
- auth/user context placeholder,
- call service layer,
- return typed response.

### Service Layer

Business workflows.

Examples:

- create estimate,
- add assembly to estimate,
- calculate estimate,
- export BOM,
- seed catalog,
- manage snapshots.

### Domain Layer

Pure business logic.

Examples:

- pricing math,
- rule evaluation,
- formula evaluation,
- review flag generation,
- assembly expansion.

### Persistence Layer

SQLAlchemy models and repository functions.

## Frontend Layers

### App Shell

Layout, navigation, routing, page framing.

### Feature Modules

Feature modules for:

- customers,
- jobs,
- catalog,
- assemblies,
- estimates,
- exports.

### API Client

A typed API client used by TanStack Query hooks.

### Components

Reusable UI elements:

- table,
- form field,
- money display,
- status badge,
- review flag alert,
- line item table,
- export button.

## Deployment Direction

V1 local development should use Docker Compose.

Future OCI deployment can use:

- OCI Container Instances or OKE for API,
- OCI Object Storage for static frontend and attachments/exports,
- Postgres-compatible database or self-managed Postgres on Compute,
- OCI Vault for secrets,
- OCI Logging and Monitoring.

Do not overbuild deployment in V1. Make the app container-friendly.

## Estimate Calculation Flow

```text
Load estimate
Load selected assemblies and parameters
Load margin profile
For each assembly:
  add base material lines
  add base labor lines
  evaluate rules
  add rule-generated lines and notes
Generate review flags
Calculate totals
Persist snapshot
Return estimate result
```

## Snapshot Strategy

When an estimate is calculated, persist a snapshot containing:

```json
{
  "margin_profile": {},
  "assemblies": [],
  "materials": [],
  "labor_units": [],
  "rules": [],
  "parameters": {},
  "totals": {},
  "assumptions": [],
  "exclusions": [],
  "review_flags": []
}
```

The snapshot is the historical record. Catalog changes after calculation must not alter previously calculated estimates.
