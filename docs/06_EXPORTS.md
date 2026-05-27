# Exports

## Export Types

V1 must support:

1. Supplier BOM CSV.
2. Internal BOM CSV.
3. Client PDF.

## Supplier BOM CSV

Audience: supplier or purchasing contact.

Must exclude:

- labor pricing,
- labor hours,
- markup,
- margin,
- profit,
- overhead,
- internal review flags.

Columns:

```text
SKU
Description
Quantity
Unit
Manufacturer
Supplier
Notes
```

Only include material/equipment items relevant to purchasing.

## Internal BOM CSV

Audience: owner, estimator, internal team.

Columns:

```text
Line Type
Source Type
Source Assembly
SKU
Description
Quantity
Unit
Unit Cost
Unit Sell
Total Cost
Total Sell
Labor Hours
Rule Applied
Notes
```

Include both material and labor lines.

## Client PDF

Audience: client/internal review.

Sections:

1. Contractor/company header placeholder.
2. Customer details.
3. Job/site details.
4. Scope summary.
5. Price summary.
6. Included work.
7. Assumptions.
8. Exclusions.
9. Review/disclaimer language.
10. Optional signature/approval block.

Required disclaimer:

```text
This estimate is based on the information provided and listed assumptions. Final installation is subject to field verification, applicable code requirements, utility requirements, and AHJ approval. This estimate is not a substitute for code compliance review or AHJ approval.
```

## Client PDF Pricing Detail

Default V1 client PDF should show a summary price, not every internal cost.

Recommended sections:

```text
Material and equipment
Labor
Fees/allowances
Total estimate
```

Do not expose internal margin percentages by default.

## File Naming

Use predictable names:

```text
estimate-{estimate_number}-supplier-bom.csv
estimate-{estimate_number}-internal-bom.csv
estimate-{estimate_number}-client.pdf
```

If no estimate number exists, use estimate UUID prefix and date.

## Export Storage

For local V1:

```text
storage/exports/
```

Future OCI deployment:

```text
OCI Object Storage bucket
```

Persist export metadata in `estimate_exports`.
