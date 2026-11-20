---
identity:
  atom_id: CA-D-723
  ref_id: CA-D-723
context:
  role: delivery
  form: decision
  container:
    scope_unit: CA-SU-45
  tier: 5
  topics:
    main_subject: PROJECT STRUCTURE//ANECHOIC <+ Aspects <+ Engineering <+ Operation
      <+ Data Handling <+ Schema
    dependencies:
    - MODEL//ANECHOIC <+ Projection
relations:
  SPECIALIZES:
  - CA-D-672
state:
  version: 1
  status: active
  updated_at: '2026-11-13T19:27:40.868534+00:00'
destination:
  file:
    name: CA-D-723-WORKBENCH_BACKEND-DECISION--deliver-one-sql-row-per-atom-carrier.md
    path: .anechoic_anechoic/CA-SU-14_LAYER_2_FRAMEWORK_ENGINE/CA-SU-15_FEATURE_PROGRAMMATIC/CA-SU-20_FEATURE_APPS/CA-SU-43_APP_WORKBENCH/CA-SU-45_FEATURE_WORKBENCH_BACKEND/07_delivery
---
## Summary

Deliver one SQL row per Atom carrier

## Claim scope

The Workbench `atoms` table.

## Claim

### Prose Claim

Key `atoms` by `(relative_path, filename)` so readable carriers with the same logical identity remain separate rows. Publish typed Header and Content columns, one projected `header.relations` JSON value and a deterministic hash of each row excluding its hash field.
