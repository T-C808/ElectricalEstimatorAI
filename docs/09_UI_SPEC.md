# UI Spec

## Design Goal

The UI should feel practical and trustworthy. It is for small electrical contractors, not enterprise procurement teams.

Prioritize:

- speed,
- clarity,
- traceability,
- editable catalogs,
- obvious review warnings,
- clean exports.

## Navigation

Recommended left nav:

```text
Dashboard
Customers
Jobs
Estimates
Catalog
  Materials
  Labor
  Margins
Assemblies
Settings
```

## Dashboard

Show:

- recent jobs,
- recent estimates,
- estimates requiring review,
- quick action: New Job,
- quick action: New Estimate.

## Customer Pages

### Customer List

Columns:

```text
Company
Contact
Phone
Email
Open Jobs
Updated
```

### Customer Detail

Sections:

- customer information,
- notes,
- jobs.

## Job Detail

Sections:

- customer summary,
- site details,
- job notes,
- attachments metadata,
- estimates for this job,
- create estimate button.

## Catalog Pages

### Materials

Columns:

```text
SKU
Name
Category
Unit
Unit Cost
Markup
Supplier
Active
```

Actions:

- create,
- edit,
- deactivate,
- import CSV if implemented.

### Labor Units

Columns:

```text
Code
Name
Base Hours
Crew Size
Difficulty
Active
```

### Margin Profiles

Columns:

```text
Name
Material Markup
Labor Rate
Overhead
Profit
Contingency
Tax
Active
```

## Assembly Library

Columns:

```text
Code
Name
Version
Category
Active
```

Assembly detail should show:

- parameters,
- base materials,
- base labor,
- rules,
- assumptions,
- exclusions.

## Estimate Builder

The estimate builder is the most important screen.

Suggested layout:

```text
Header: Job / Customer / Status / Margin Profile
Left Panel: Assembly selection
Center: Selected assemblies and parameters
Right Panel: Estimate summary and review flags
Bottom: Line items, assumptions, exclusions, exports
```

### Estimate Builder Must Show

- selected assemblies,
- required parameters,
- missing parameter validation,
- calculate button,
- line item table,
- totals,
- assumptions,
- exclusions,
- review flags,
- export buttons.

### Line Item Table Columns

```text
Type
Source
SKU/Code
Description
Qty
Unit
Unit Cost
Unit Sell
Total Sell
Notes
```

For a client-safe display, hide unit cost and internal details.

## Review Flags

Use clear labels:

```text
Info
Warning
Critical
```

Examples:

- `ATS included - owner review required.`
- `Shutdown required - confirm schedule and utility requirements.`
- `Feeder length missing - estimate cannot be trusted.`
- `Manual override used - verify pricing before sending.`

## Empty States

Useful empty states:

- No customers yet. Create customer.
- No jobs yet. Create job.
- No assemblies selected. Add an assembly to begin estimate.
- Missing required parameters. Complete fields before calculating.

## Formatting

- Money: `$12,345.67`
- Percentages: `25%`
- Hours: `8.0 hrs`
- Quantities: show up to 3 decimals when needed.

## Accessibility

- Use semantic buttons and form labels.
- Do not rely only on color for review flags.
- Keep tables keyboard-navigable where practical.
