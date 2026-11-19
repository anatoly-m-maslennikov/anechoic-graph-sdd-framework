---
identity:
  atom_id: CA-M-1027
  ref_id: CA-M-1027
context:
  role: method
  form: decision
  container:
    scope_unit: CA-SU-45
  tier: 5
  topics:
    main_subject: PROJECT STRUCTURE//ANECHOIC <+ Aspects <+ Engineering <+ Operation
      <+ Data Handling <+ Indexing
    dependencies:
    - MODEL//ANECHOIC <+ Projection
relations:
  SPECIALIZES:
  - CA-M-465
state:
  version: 1
  status: active
  updated_at: '2026-11-13T19:27:59.851737+00:00'
destination:
  file:
    name: CA-M-1027-WORKBENCH_BACKEND-DECISION--publish-completed-lifecycle-writes-in-one-workbench-refresh.md
    path: .anechoic_anechoic/CA-SU-14_LAYER_2_FRAMEWORK_ENGINE/CA-SU-15_FEATURE_PROGRAMMATIC/CA-SU-20_FEATURE_APPS/CA-SU-43_APP_WORKBENCH/CA-SU-45_FEATURE_WORKBENCH_BACKEND/05_method
---
## Summary

Publish completed lifecycle writes in one Workbench refresh

## Claim scope

Independent lifecycle batch targets.

## Claim

### Prose Claim

Collect the paths changed by independent Archive or Promote Draft targets and refresh them together. Include completed file effects when a later target fails. Report a publication error separately when the files were written but Workbench could not refresh them.
