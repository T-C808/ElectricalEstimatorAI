# Product Brief

## Product Name

Working name: Electrical Estimator + BOM Engine

## Target User

Small electrical contractors:

- owner-led,
- 2 to 5 technicians,
- estimating manually in spreadsheets,
- repeating similar jobs,
- needs faster supplier-ready BOM creation.

## Positioning

A junior estimator for small electrical shops.

The app turns site inputs, catalog pricing, reusable assemblies, and deterministic rules into a priced estimate and BOM.

## Core Workflow

```text
Intake -> Estimate -> BOM Export
```

### Intake

User creates a customer and job. The job stores site details, notes, constraints, existing equipment info, attachments metadata, and relevant requirements such as shutdown or NETA testing.

### Estimate

User selects assemblies such as ATS install, panel upgrade, or feeder run. User enters parameters such as feeder length, conduit type, service size, indoor/outdoor, shutdown required, and testing requirements.

The system applies catalog pricing, labor units, margins, and rules.

### BOM Export

The system outputs supplier CSV, internal CSV, and client/internal PDF.

## Core Value

- Saves quote-building time.
- Standardizes repeatable pricing.
- Reduces forgotten material items.
- Produces a clean supplier-ready BOM.
- Creates a traceable estimate that an owner can review.

## V1 Feature Set

1. Customer and job records.
2. Material catalog.
3. Labor catalog.
4. Margin profiles.
5. Assembly templates.
6. Rule-based quantity/labor adjustments.
7. Estimate generation.
8. Estimate snapshotting.
9. Supplier BOM CSV.
10. Internal BOM CSV.
11. Client PDF.
12. Guardrails: assumptions, exclusions, review flags, code/AHJ disclaimer.

## Trust Requirements

The app must be explicit about where numbers come from.

Each line item should indicate whether it came from:

- manual entry,
- assembly base item,
- rule action.

The app must show:

- assumptions,
- exclusions,
- review flags,
- pricing summary,
- current margin profile,
- assembly versions used.

## V1 Success Criteria

A contractor can price a basic ATS/panel/feeder job without building the BOM from scratch and can export a supplier-ready list in minutes.
