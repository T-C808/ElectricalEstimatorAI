# Rules Engine

## Goal

The rules engine adjusts assemblies based on user-provided job parameters.

It must be deterministic, easy to test, and safe. Do not execute arbitrary code.

## Supported Condition Operators

```text
equals
not_equals
greater_than
greater_than_or_equal
less_than
less_than_or_equal
in
exists
```

## Supported Action Types

```text
add_material
add_labor
multiply_labor
add_note
add_exclusion
add_assumption
require_review
```

## Rule Shape

```json
{
  "id": "rigid-conduit-labor-factor",
  "name": "Rigid conduit labor factor",
  "when": {
    "field": "conduit_type",
    "operator": "equals",
    "value": "RIGID"
  },
  "actions": [
    {
      "type": "multiply_labor",
      "target": "conduit_install_labor",
      "factor": 1.35
    },
    {
      "type": "add_note",
      "note_type": "assumption",
      "note": "Rigid conduit selected; labor increased for installation difficulty."
    }
  ]
}
```

## Compound Conditions

V1 may support simple `all` and `any` groups:

```json
{
  "all": [
    {
      "field": "service_size_amps",
      "operator": "greater_than_or_equal",
      "value": 400
    },
    {
      "field": "shutdown_required",
      "operator": "equals",
      "value": true
    }
  ]
}
```

If compound conditions slow down delivery, implement simple conditions first and document the limitation.

## Formula Evaluation

Formula examples:

```text
feeder_length_ft * conductor_count * waste_factor
feeder_length_ft * conduit_count * 1.05
base_hours * difficulty_factor
```

Allowed variables:

```text
feeder_length_ft
conductor_count
conduit_count
waste_factor
crew_size
difficulty_factor
base_hours
```

Allowed operators:

```text
+ - * / ( )
```

Do not allow:

- function calls,
- attribute access,
- imports,
- string interpolation,
- raw Python eval,
- JavaScript eval,
- SQL fragments.

## Required Rule Tests

Add tests for:

1. `equals` condition true/false.
2. numeric comparison true/false.
3. missing field behavior.
4. `in` behavior.
5. add material action.
6. add labor action.
7. multiply labor action.
8. add assumption/exclusion/note action.
9. require review action.
10. formula rejects unsafe expressions.
11. formula evaluates approved expressions.

## Starter Rules

### Feeder Length Adds Conductors

```json
{
  "id": "feeder-conductors-by-length",
  "name": "Feeder conductors by length",
  "when": {
    "field": "feeder_length_ft",
    "operator": "greater_than",
    "value": 0
  },
  "actions": [
    {
      "type": "add_material",
      "material_sku": "FEEDER-CONDUCTOR-600A",
      "quantity_formula": "feeder_length_ft * conductor_count * waste_factor",
      "unit": "ft"
    }
  ]
}
```

### Rigid Conduit Labor Factor

```json
{
  "id": "rigid-conduit-labor-factor",
  "name": "Rigid conduit labor factor",
  "when": {
    "field": "conduit_type",
    "operator": "equals",
    "value": "RIGID"
  },
  "actions": [
    {
      "type": "multiply_labor",
      "target": "conduit_install_labor",
      "factor": 1.35
    },
    {
      "type": "add_assumption",
      "note": "Rigid conduit selected; labor increased for installation difficulty."
    }
  ]
}
```

### Shutdown Required

```json
{
  "id": "shutdown-coordination-required",
  "name": "Shutdown coordination required",
  "when": {
    "field": "shutdown_required",
    "operator": "equals",
    "value": true
  },
  "actions": [
    {
      "type": "add_labor",
      "labor_code": "SHUTDOWN-COORD",
      "hours": 4
    },
    {
      "type": "require_review",
      "flag_code": "SHUTDOWN_REQUIRED",
      "severity": "warning",
      "message": "Shutdown required. Confirm schedule, customer impact, and utility requirements."
    }
  ]
}
```

### NETA Testing Selected

```json
{
  "id": "neta-testing-selected",
  "name": "NETA testing selected",
  "when": {
    "field": "neta_testing_required",
    "operator": "equals",
    "value": true
  },
  "actions": [
    {
      "type": "add_labor",
      "labor_code": "NETA-SUPPORT",
      "hours": 8
    },
    {
      "type": "add_exclusion",
      "note": "Third-party NETA testing fees are excluded unless separately listed."
    },
    {
      "type": "require_review",
      "flag_code": "NETA_TESTING_SELECTED",
      "severity": "warning",
      "message": "NETA testing selected. Confirm third-party testing scope and fees."
    }
  ]
}
```
