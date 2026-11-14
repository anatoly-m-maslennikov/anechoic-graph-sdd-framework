---
identity:
  atom_id: CA-D-725
  ref_id: CA-D-725@2-draft
context:
  role: delivery
  form: decision
  container:
    scope_unit: CA-SU-45
  tier: 5
  topics:
    main_subject: PROJECT STRUCTURE//CAPRMEDIO <+ Aspects <+ Engineering <+ Operation
      <+ Storage <+ Temporary State
    dependencies:
    - MODEL//CAPRMEDIO <+ Projection
relations:
  SPECIALIZES:
  - CA-D-675
  IS_REPLACEMENT_FOR:
  - CA-D-725
state:
  version: 2
  status: draft
  updated_at: '2026-11-14T00:32:36.680503+00:00'
destination:
  file:
    name: CA-D-725@2-draft-WORKBENCH_BACKEND-DECISION--read-the-workbench-result-ttl-at-startup.md
    path: .caprmedio_caprmedio/CA-SU-14_LAYER_2_FRAMEWORK_ENGINE/CA-SU-15_FEATURE_PROGRAMMATIC/CA-SU-20_FEATURE_APPS/CA-SU-43_APP_WORKBENCH/CA-SU-45_FEATURE_WORKBENCH_BACKEND/07_delivery/000_draft
---
## Summary

Read the Workbench result TTL at startup

## Claim

### Prose Claim

Read `workbench.result_ttl_seconds` at Workbench Backend startup from
`.caprmedio_runtime/caprmedio_runtime_settings.toml`.

## Details

- Use 3,600 seconds when the setting is absent.
- Reject an unreadable or invalid settings file.
- Reject a TTL that is not a positive integer.
