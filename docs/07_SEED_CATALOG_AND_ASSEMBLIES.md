# Seed Catalog and Assemblies

## Purpose

Provide enough seed data for a developer or demo user to create a realistic estimate without manually building the catalog first.

Prices below are placeholders. The UI should clearly allow owner-controlled edits.

## Seed Margin Profile

```json
{
  "name": "Default Small Contractor Margin",
  "material_markup_percent": 0.25,
  "labor_rate_per_hour": 125.00,
  "overhead_percent": 0.10,
  "profit_percent": 0.15,
  "contingency_percent": 0.05,
  "tax_percent": 0.00,
  "minimum_margin_percent": 0.10,
  "active": true
}
```

## Seed Materials

```json
[
  {
    "sku": "ATS-600-BYPASS",
    "name": "600A Automatic Transfer Switch with Bypass",
    "category": "ATS",
    "unit": "each",
    "unit_cost": 18500.00,
    "default_markup_percent": 0.25,
    "supplier": "TBD",
    "manufacturer": "TBD"
  },
  {
    "sku": "ATS-400",
    "name": "400A Automatic Transfer Switch",
    "category": "ATS",
    "unit": "each",
    "unit_cost": 9800.00,
    "default_markup_percent": 0.25,
    "supplier": "TBD",
    "manufacturer": "TBD"
  },
  {
    "sku": "PANEL-NEMA-3R",
    "name": "NEMA 3R Panelboard Allowance",
    "category": "Panel",
    "unit": "each",
    "unit_cost": 4200.00,
    "default_markup_percent": 0.25,
    "supplier": "TBD",
    "manufacturer": "TBD"
  },
  {
    "sku": "PANEL-NEMA-3RX",
    "name": "NEMA 3RX Panelboard Allowance",
    "category": "Panel",
    "unit": "each",
    "unit_cost": 5200.00,
    "default_markup_percent": 0.25,
    "supplier": "TBD",
    "manufacturer": "TBD"
  },
  {
    "sku": "CONDUIT-EMT-2IN",
    "name": "2 inch EMT conduit",
    "category": "Conduit",
    "unit": "ft",
    "unit_cost": 4.75,
    "default_markup_percent": 0.25,
    "supplier": "TBD",
    "manufacturer": "TBD"
  },
  {
    "sku": "CONDUIT-PVC-2IN",
    "name": "2 inch PVC conduit",
    "category": "Conduit",
    "unit": "ft",
    "unit_cost": 3.60,
    "default_markup_percent": 0.25,
    "supplier": "TBD",
    "manufacturer": "TBD"
  },
  {
    "sku": "CONDUIT-RIGID-2IN",
    "name": "2 inch rigid conduit",
    "category": "Conduit",
    "unit": "ft",
    "unit_cost": 12.50,
    "default_markup_percent": 0.25,
    "supplier": "TBD",
    "manufacturer": "TBD"
  },
  {
    "sku": "FEEDER-CONDUCTOR-600A",
    "name": "600A feeder conductor allowance",
    "category": "Wire",
    "unit": "ft",
    "unit_cost": 14.50,
    "default_markup_percent": 0.25,
    "supplier": "TBD",
    "manufacturer": "TBD"
  },
  {
    "sku": "GROUND-LUG-KIT",
    "name": "Grounding lug kit",
    "category": "Grounding",
    "unit": "kit",
    "unit_cost": 185.00,
    "default_markup_percent": 0.25,
    "supplier": "TBD",
    "manufacturer": "TBD"
  },
  {
    "sku": "LABEL-KIT-ELECTRICAL",
    "name": "Electrical label kit",
    "category": "Labels",
    "unit": "kit",
    "unit_cost": 95.00,
    "default_markup_percent": 0.25,
    "supplier": "TBD",
    "manufacturer": "TBD"
  },
  {
    "sku": "PULL-BOX-ALLOWANCE",
    "name": "Pull box allowance",
    "category": "Boxes",
    "unit": "each",
    "unit_cost": 650.00,
    "default_markup_percent": 0.25,
    "supplier": "TBD",
    "manufacturer": "TBD"
  }
]
```

## Seed Labor Units

```json
[
  {
    "code": "INSTALL-ATS-600",
    "name": "Install 600A ATS",
    "description": "Set, mount, and prepare 600A ATS for terminations.",
    "base_hours": 16,
    "crew_size": 2,
    "difficulty_factor": 1
  },
  {
    "code": "INSTALL-ATS-400",
    "name": "Install 400A ATS",
    "description": "Set, mount, and prepare 400A ATS for terminations.",
    "base_hours": 12,
    "crew_size": 2,
    "difficulty_factor": 1
  },
  {
    "code": "INSTALL-PANEL",
    "name": "Install panelboard",
    "description": "Install panelboard allowance.",
    "base_hours": 10,
    "crew_size": 2,
    "difficulty_factor": 1
  },
  {
    "code": "CONDUIT-INSTALL-PER-FT",
    "name": "Install conduit per foot",
    "description": "Generic conduit install labor per foot.",
    "base_hours": 0.08,
    "crew_size": 1,
    "difficulty_factor": 1
  },
  {
    "code": "PULL-FEEDER-PER-FT",
    "name": "Pull feeder conductors per foot",
    "description": "Feeder pulling labor per route foot.",
    "base_hours": 0.06,
    "crew_size": 2,
    "difficulty_factor": 1
  },
  {
    "code": "TERMINATE-FEEDERS-600A",
    "name": "Terminate 600A feeders",
    "description": "Terminate feeder conductors at equipment.",
    "base_hours": 8,
    "crew_size": 2,
    "difficulty_factor": 1
  },
  {
    "code": "SHUTDOWN-COORD",
    "name": "Shutdown coordination",
    "description": "Coordinate customer/utility shutdown window.",
    "base_hours": 4,
    "crew_size": 1,
    "difficulty_factor": 1
  },
  {
    "code": "NETA-SUPPORT",
    "name": "NETA testing support",
    "description": "Electrical contractor support for third-party testing.",
    "base_hours": 8,
    "crew_size": 1,
    "difficulty_factor": 1
  },
  {
    "code": "GROUNDING-BONDING",
    "name": "Grounding and bonding allowance",
    "description": "Grounding and bonding labor allowance.",
    "base_hours": 6,
    "crew_size": 1,
    "difficulty_factor": 1
  }
]
```

## Common Assembly Parameters

```json
[
  {
    "name": "service_size_amps",
    "type": "number",
    "required": true
  },
  {
    "name": "feeder_length_ft",
    "type": "number",
    "required": true
  },
  {
    "name": "conduit_type",
    "type": "enum",
    "options": ["EMT", "PVC", "RIGID"],
    "required": true
  },
  {
    "name": "conductor_count",
    "type": "number",
    "required": true,
    "default": 4
  },
  {
    "name": "waste_factor",
    "type": "number",
    "required": true,
    "default": 1.1
  },
  {
    "name": "shutdown_required",
    "type": "boolean",
    "required": true,
    "default": false
  },
  {
    "name": "neta_testing_required",
    "type": "boolean",
    "required": true,
    "default": false
  },
  {
    "name": "existing_equipment_known",
    "type": "boolean",
    "required": true,
    "default": false
  }
]
```

## Assembly: ATS-600-BYPASS

```json
{
  "code": "ATS-600-BYPASS",
  "name": "600A ATS Install with Bypass",
  "version": 1,
  "category": "ATS",
  "base_materials": [
    { "sku": "ATS-600-BYPASS", "quantity_formula": "1", "unit": "each" },
    { "sku": "GROUND-LUG-KIT", "quantity_formula": "1", "unit": "kit" },
    { "sku": "LABEL-KIT-ELECTRICAL", "quantity_formula": "1", "unit": "kit" }
  ],
  "base_labor": [
    { "code": "INSTALL-ATS-600", "hours_formula": "base_hours" },
    { "code": "TERMINATE-FEEDERS-600A", "hours_formula": "base_hours" }
  ],
  "assumptions": [
    "Existing gear is suitable for reuse unless otherwise noted.",
    "Normal working hours unless shutdown coordination is selected.",
    "Estimate assumes clear working access to equipment."
  ],
  "exclusions": [
    "Permits and AHJ fees unless explicitly included.",
    "Utility company fees.",
    "Engineering studies unless explicitly included.",
    "Unforeseen code corrections."
  ]
}
```

## Assembly: FEEDER-EMT

```json
{
  "code": "FEEDER-EMT",
  "name": "Feeder Run - EMT",
  "version": 1,
  "category": "Feeder",
  "base_materials": [
    { "sku": "CONDUIT-EMT-2IN", "quantity_formula": "feeder_length_ft * 1.05", "unit": "ft" },
    { "sku": "FEEDER-CONDUCTOR-600A", "quantity_formula": "feeder_length_ft * conductor_count * waste_factor", "unit": "ft" }
  ],
  "base_labor": [
    { "code": "CONDUIT-INSTALL-PER-FT", "hours_formula": "base_hours * feeder_length_ft" },
    { "code": "PULL-FEEDER-PER-FT", "hours_formula": "base_hours * feeder_length_ft" }
  ],
  "assumptions": [
    "Feeder route length is based on provided field input.",
    "Standard supports and fittings are included as an allowance only."
  ],
  "exclusions": [
    "Core drilling, trenching, and concrete repair are excluded unless separately listed."
  ]
}
```

## Assembly: FEEDER-PVC

Same as `FEEDER-EMT`, but use material `CONDUIT-PVC-2IN` and add assumption:

```text
PVC conduit selected; estimate assumes installation conditions suitable for PVC.
```

## Assembly: FEEDER-RIGID

Same as `FEEDER-EMT`, but use material `CONDUIT-RIGID-2IN` and apply rigid conduit labor factor rule.

## Assembly: SHUTDOWN-COORD

```json
{
  "code": "SHUTDOWN-COORD",
  "name": "Shutdown Coordination Allowance",
  "version": 1,
  "category": "Coordination",
  "base_materials": [],
  "base_labor": [
    { "code": "SHUTDOWN-COORD", "hours_formula": "base_hours" }
  ],
  "assumptions": [
    "Includes coordination allowance only. Final shutdown schedule requires customer and utility approval."
  ],
  "exclusions": [
    "Utility fees and after-hours premiums are excluded unless separately listed."
  ]
}
```

## Assembly: NETA-SUPPORT

```json
{
  "code": "NETA-SUPPORT",
  "name": "NETA Testing Support Allowance",
  "version": 1,
  "category": "Testing",
  "base_materials": [],
  "base_labor": [
    { "code": "NETA-SUPPORT", "hours_formula": "base_hours" }
  ],
  "assumptions": [
    "Includes electrical contractor support time only."
  ],
  "exclusions": [
    "Third-party NETA testing fees are excluded unless separately listed."
  ]
}
```
