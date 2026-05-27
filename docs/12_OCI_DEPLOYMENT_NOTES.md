# OCI Deployment Notes

This is not required for the first local MVP, but the code should be container-friendly.

## Simple OCI Target Architecture

```text
React static build -> OCI Object Storage static hosting or container
FastAPI API -> OCI Container Instances or Compute
Postgres -> managed Postgres-compatible option or self-managed Postgres on Compute
Files/exports -> OCI Object Storage
Secrets -> OCI Vault
Logs -> OCI Logging
Metrics -> OCI Monitoring
```

## Environment Variables

Backend should support:

```text
DATABASE_URL
APP_ENV
CORS_ORIGINS
STORAGE_BACKEND
LOCAL_STORAGE_PATH
OCI_OBJECT_STORAGE_BUCKET
OCI_REGION
OCI_NAMESPACE
```

Do not require OCI credentials for local development.

## Container Requirements

- API should expose port 8000.
- Frontend dev server should expose port 5173 locally.
- Production frontend can be static build.
- Health endpoint should be available at `/api/v1/health`.

## Future Object Storage Abstraction

Create a storage interface if implementing attachments or export persistence:

```text
StorageService.save_file(bytes, key, content_type)
StorageService.get_download_url(key)
StorageService.delete_file(key)
```

V1 implementations:

- LocalFileStorage for local dev.
- OCIObjectStorage later.

## Future Security

Use OCI Vault for:

- database password,
- object storage credentials if not using instance principals,
- signing keys,
- third-party auth secrets.

Prefer instance principals or workload identity for OCI services where possible.
