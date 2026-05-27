# Testing Strategy

## Backend Tests

Use pytest.

### Unit Tests

Pricing math:

- material sell calculation,
- labor sell calculation,
- overhead calculation,
- profit calculation,
- contingency calculation,
- grand total calculation,
- rounding behavior.

Rules engine:

- condition operators,
- safe formulas,
- unsafe formula rejection,
- add material action,
- add labor action,
- multiply labor action,
- add note action,
- add assumption action,
- add exclusion action,
- require review action.

Estimate generation:

- assembly base material expansion,
- assembly base labor expansion,
- rule-generated lines,
- assumptions/exclusions collection,
- review flag generation,
- snapshot persistence.

Exports:

- supplier CSV excludes internal pricing,
- internal CSV includes cost/sell values,
- client PDF includes disclaimer.

### Integration Tests

- Create customer.
- Create job.
- Create estimate.
- Add assembly.
- Calculate estimate.
- Export CSV.

## Frontend Tests

Use Vitest and React Testing Library if practical.

Tests:

- customer form validation,
- material form validation,
- estimate builder required parameter validation,
- selected assembly appears in estimate builder,
- totals render after calculation,
- review flags render,
- export buttons appear for calculated estimate.

## Smoke Test Script

Manual smoke test:

1. Start local app.
2. Seed data.
3. Open dashboard.
4. Create customer: `Demo Customer`.
5. Create job: `600A ATS Demo`.
6. Create estimate.
7. Select margin profile: `Default Small Contractor Margin`.
8. Add assembly: `ATS-600-BYPASS`.
9. Add assembly: `FEEDER-EMT`.
10. Enter feeder length: `125`.
11. Enter service size: `600`.
12. Select conduit type: `EMT`.
13. Set shutdown required: `true`.
14. Set NETA testing required: `false`.
15. Calculate estimate.
16. Confirm review flags show ATS, service size, and shutdown.
17. Export supplier CSV.
18. Export internal CSV.
19. Export client PDF.
20. Confirm client PDF contains required disclaimer.
