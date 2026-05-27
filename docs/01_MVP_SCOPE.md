# MVP Scope

## In Scope

### Customer Management

- Create customer.
- Edit customer.
- List customers.
- View customer detail.

### Job Management

- Create job for customer.
- Edit job.
- Track status.
- Store site notes and scope notes.
- Store attachment metadata.

### Catalog Management

- Material CRUD.
- Labor unit CRUD.
- Margin profile CRUD.
- Active/inactive states.

### Assembly Library

- Versioned assemblies.
- Assembly parameters.
- Assembly base materials.
- Assembly base labor.
- Assembly rules.
- Assembly assumptions.
- Assembly exclusions.

### Estimate Builder

- Create estimate for job.
- Select margin profile.
- Add assemblies.
- Configure assembly parameters.
- Calculate estimate.
- View material, labor, subtotal, overhead, profit, contingency, tax, and total.
- View line items.
- View assumptions, exclusions, and review flags.
- Export supplier CSV, internal CSV, and client PDF.

### Guardrails

- Required disclaimer.
- Human review requirement.
- Review flags.
- Snapshotting.

## Out of Scope

- Service scheduling.
- Dispatch board.
- Technician mobile app.
- Inventory decrementing.
- Supplier purchasing integration.
- QuickBooks integration.
- Stripe payments.
- Customer portal.
- Full NEC validation.
- Permit filing.
- Utility application automation.

## User Roles for V1

Keep roles simple.

```text
owner
estimator
viewer
```

For local V1, authentication can be stubbed with a dev user. Design the data model so real auth can be added later.

## Core Screens

1. Dashboard.
2. Customers list.
3. Customer detail.
4. Job detail.
5. Materials catalog.
6. Labor catalog.
7. Margin profiles.
8. Assembly library.
9. Estimate builder.
10. Estimate review.
11. Export/download panel.

## Critical V1 Path

```text
Create customer -> Create job -> Add ATS assembly -> Enter feeder length and conduit type -> Calculate -> Review -> Export CSV/PDF
```
