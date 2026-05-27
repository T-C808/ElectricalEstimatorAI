# Guardrails and Security

## Estimating Guardrails

Every estimate must include:

- assumptions,
- exclusions,
- human review requirement,
- code/AHJ disclaimer,
- review flags when triggered.

## Required Disclaimer

```text
This estimate is based on the information provided and listed assumptions. Final installation is subject to field verification, applicable code requirements, utility requirements, and AHJ approval. This estimate is not a substitute for code compliance review or AHJ approval.
```

## Review Flag Conditions

Trigger review for:

```text
service_size_amps >= 400
ATS included
generator interconnection included
neta_testing_required = true
shutdown_required = true
utility_coordination_required = true
existing_equipment_known = false
feeder_length_ft missing
conduit_type missing
manual override used
margin below minimum threshold
```

## Formula Safety

Never run arbitrary code from catalog, assembly, or user input.

Do not use:

- Python `eval`,
- Python `exec`,
- JavaScript `eval`,
- dynamic imports,
- SQL fragments,
- shell commands.

Use a parsed AST or small expression parser with whitelisted tokens.

## Data Safety

- Do not store secrets in code.
- Use environment variables for database URL and future object storage credentials.
- Use local `.env` only for development.
- Add `.env` to `.gitignore`.
- Do not include supplier credentials or real customer data in seed files.

## Authorization Direction

V1 can use a dev user, but code should be structured for future auth.

Future role behavior:

```text
owner: full access, margins, exports, overrides
estimator: create/edit jobs and estimates, limited margin profile access
viewer: read-only
```

## Audit Requirements for Later

The following should be designed in a way that audit trails can be added later:

- price overrides,
- margin profile changes,
- catalog cost updates,
- assembly version updates,
- estimate approval,
- export generation.

For V1, at minimum store `created_at` and `updated_at`. If easy, also store `created_by` and `updated_by`.
