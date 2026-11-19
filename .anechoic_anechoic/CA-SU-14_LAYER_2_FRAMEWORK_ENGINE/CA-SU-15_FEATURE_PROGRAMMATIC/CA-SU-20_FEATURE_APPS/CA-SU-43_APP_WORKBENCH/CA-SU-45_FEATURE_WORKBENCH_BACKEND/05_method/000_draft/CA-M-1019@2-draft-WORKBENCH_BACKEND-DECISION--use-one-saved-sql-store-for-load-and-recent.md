---
identity:
  atom_id: CA-M-1019
  ref_id: CA-M-1019@2-draft
context:
  role: method
  form: decision
  container:
    scope_unit: CA-SU-45
  tier: 4
  topics:
    main_subject: MODEL//ANECHOIC <+ Projection
relations:
  SPECIALIZES:
  - CA-R-2776@10
  IS_REPLACEMENT_FOR:
  - CA-M-1019
state:
  version: 2
  status: draft
  updated_at: '2026-11-14T07:53:20.785754+00:00'
destination:
  file:
    name: CA-M-1019@2-draft-WORKBENCH_BACKEND-DECISION--use-one-saved-sql-store-for-load-and-recent.md
    path: .anechoic_anechoic/CA-SU-14_LAYER_2_FRAMEWORK_ENGINE/CA-SU-15_FEATURE_PROGRAMMATIC/CA-SU-20_FEATURE_APPS/CA-SU-43_APP_WORKBENCH/CA-SU-45_FEATURE_WORKBENCH_BACKEND/05_method/000_draft
---
## Summary

Use one saved SQL store for Load and Recent

## Claim

### Prose Claim

Use one saved SQL store for Workbench Load and Recent.
Load reads stored SQL. Recent reads the same store for item metadata.
