---
identity:
  atom_id: CA-D-726
  ref_id: CA-D-726
context:
  role: delivery
  form: decision
  container:
    scope_unit: CA-SU-46
  tier: 6
  topics:
    main_subject: PROJECT STRUCTURE//CAPRMEDIO <+ Aspects <+ Engineering <+ Development
      <+ Architecture <+ Communication <+ Interface Contracts
    dependencies:
    - MODEL//CAPRMEDIO <+ Projection
relations:
  SPECIALIZES:
  - CA-D-718
state:
  version: 1
  status: active
  updated_at: '2026-11-13T19:27:55.760142+00:00'
destination:
  file:
    name: CA-D-726-WORKBENCH_FRONTEND-DECISION--load-selected-archive-scopes-from-the-workbench-dialog.md
    path: .caprmedio_caprmedio/CA-SU-14_LAYER_2_FRAMEWORK_ENGINE/CA-SU-15_FEATURE_PROGRAMMATIC/CA-SU-20_FEATURE_APPS/CA-SU-43_APP_WORKBENCH/CA-SU-46_FEATURE_WORKBENCH_FRONTEND/07_delivery
---
## Summary

Load selected Archive scopes from the Workbench dialog

## Claim scope

The Workbench Archive load dialog.

## Claim

### Prose Claim

Submit one or more nonempty Scope Unit and Role pairs selected by the user. Show the Archive scopes already loaded and display a failed load in the dialog.
