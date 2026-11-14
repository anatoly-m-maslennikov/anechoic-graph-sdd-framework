---
identity:
  atom_id: CA-D-724
  ref_id: CA-D-724
context:
  role: delivery
  form: decision
  container:
    scope_unit: CA-SU-45
  tier: 5
  topics:
    main_subject: PROJECT STRUCTURE//CAPRMEDIO <+ Aspects <+ Engineering <+ Development
      <+ Architecture <+ Communication <+ Interface Contracts
    dependencies:
    - MODEL//CAPRMEDIO <+ Projection
relations:
  SPECIALIZES:
  - CA-D-673
state:
  version: 1
  status: active
  updated_at: '2026-11-13T19:27:47.255416+00:00'
destination:
  file:
    name: CA-D-724-WORKBENCH_BACKEND-DECISION--deliver-cached-query-results-inline-or-as-a-file.md
    path: .caprmedio_caprmedio/CA-SU-14_LAYER_2_FRAMEWORK_ENGINE/CA-SU-15_FEATURE_PROGRAMMATIC/CA-SU-20_FEATURE_APPS/CA-SU-43_APP_WORKBENCH/CA-SU-45_FEATURE_WORKBENCH_BACKEND/07_delivery
---
## Summary

Deliver cached query results inline or as a file

## Claim scope

Workbench Run and Page result delivery.

## Claim

### Prose Claim

Deliver the requested inline page from the cached result. For file delivery, export the accepted Run result in full or only the requested Page. If export fails, keep the result ID available and report a partial outcome with the export error.
