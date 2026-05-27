# API Spec

Base path for V1:

```text
/api/v1
```

## Conventions

- JSON request/response bodies.
- UUID identifiers.
- ISO timestamps.
- Decimal money values returned as strings or numbers consistently.
- Validation errors should identify the field and reason.

## Health

```http
GET /api/v1/health
```

Response:

```json
{
  "status": "ok"
}
```

## Customers

```http
GET /api/v1/customers
POST /api/v1/customers
GET /api/v1/customers/{customer_id}
PATCH /api/v1/customers/{customer_id}
DELETE /api/v1/customers/{customer_id}
```

Soft delete is acceptable. If implementing hard delete, prevent deleting customers with jobs.

## Jobs

```http
GET /api/v1/jobs
POST /api/v1/jobs
GET /api/v1/jobs/{job_id}
PATCH /api/v1/jobs/{job_id}
DELETE /api/v1/jobs/{job_id}
GET /api/v1/customers/{customer_id}/jobs
```

## Attachments

```http
GET /api/v1/jobs/{job_id}/attachments
POST /api/v1/jobs/{job_id}/attachments
DELETE /api/v1/attachments/{attachment_id}
```

For V1, `POST` can accept metadata only if file upload is not yet implemented.

## Materials

```http
GET /api/v1/materials
POST /api/v1/materials
GET /api/v1/materials/{material_id}
PATCH /api/v1/materials/{material_id}
DELETE /api/v1/materials/{material_id}
POST /api/v1/materials/import-csv
```

Material list filters:

```text
q
category
supplier
active
```

## Labor Units

```http
GET /api/v1/labor-units
POST /api/v1/labor-units
GET /api/v1/labor-units/{labor_unit_id}
PATCH /api/v1/labor-units/{labor_unit_id}
DELETE /api/v1/labor-units/{labor_unit_id}
```

## Margin Profiles

```http
GET /api/v1/margin-profiles
POST /api/v1/margin-profiles
GET /api/v1/margin-profiles/{margin_profile_id}
PATCH /api/v1/margin-profiles/{margin_profile_id}
DELETE /api/v1/margin-profiles/{margin_profile_id}
```

Only one default active profile is optional for V1.

## Assemblies

```http
GET /api/v1/assemblies
POST /api/v1/assemblies
GET /api/v1/assemblies/{assembly_id}
PATCH /api/v1/assemblies/{assembly_id}
DELETE /api/v1/assemblies/{assembly_id}
POST /api/v1/assemblies/seed
```

Assembly list filters:

```text
q
category
active
```

## Estimates

```http
GET /api/v1/estimates
POST /api/v1/jobs/{job_id}/estimates
GET /api/v1/estimates/{estimate_id}
PATCH /api/v1/estimates/{estimate_id}
DELETE /api/v1/estimates/{estimate_id}
```

Create estimate request:

```json
{
  "margin_profile_id": "uuid"
}
```

## Estimate Assemblies

```http
GET /api/v1/estimates/{estimate_id}/assemblies
POST /api/v1/estimates/{estimate_id}/assemblies
PATCH /api/v1/estimates/{estimate_id}/assemblies/{estimate_assembly_id}
DELETE /api/v1/estimates/{estimate_id}/assemblies/{estimate_assembly_id}
```

Add assembly request:

```json
{
  "assembly_id": "uuid",
  "parameters": {
    "feeder_length_ft": 125,
    "conduit_type": "EMT",
    "shutdown_required": true,
    "neta_testing_required": false
  }
}
```

## Estimate Calculation

```http
POST /api/v1/estimates/{estimate_id}/calculate
```

Response shape:

```json
{
  "estimate_id": "uuid",
  "status": "review_required",
  "totals": {
    "material_subtotal": "0.00",
    "labor_subtotal": "0.00",
    "overhead_total": "0.00",
    "profit_total": "0.00",
    "contingency_total": "0.00",
    "tax_total": "0.00",
    "grand_total": "0.00"
  },
  "line_items": [],
  "assumptions": [],
  "exclusions": [],
  "review_flags": []
}
```

## Manual Line Items

```http
POST /api/v1/estimates/{estimate_id}/line-items
PATCH /api/v1/estimates/{estimate_id}/line-items/{line_item_id}
DELETE /api/v1/estimates/{estimate_id}/line-items/{line_item_id}
```

Manual overrides should create or update line items with `source_type = manual` and should trigger a review flag.

## Exports

```http
POST /api/v1/estimates/{estimate_id}/exports/supplier-csv
POST /api/v1/estimates/{estimate_id}/exports/internal-csv
POST /api/v1/estimates/{estimate_id}/exports/client-pdf
GET /api/v1/estimates/{estimate_id}/exports
GET /api/v1/exports/{export_id}/download
```

For local V1, return a file response directly or save generated files to local storage and return a download link.

## Seed Data

```http
POST /api/v1/dev/seed
```

Only expose this endpoint in local/development mode.
