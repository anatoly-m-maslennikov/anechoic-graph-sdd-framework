---
identity:
  atom_id: CA-D-725
  ref_id: CA-D-725
context:
  role: delivery
  form: decision
  container:
    scope_unit: CA-SU-45
  tier: 5
  topics:
    main_subject: PROJECT STRUCTURE//ANECHOIC <+ Aspects <+ Engineering <+ Operation
      <+ Storage <+ Temporary State
    dependencies:
    - MODEL//ANECHOIC <+ Projection
relations:
  SPECIALIZES:
  - CA-D-675
state:
  version: 1
  status: active
  updated_at: '2026-11-13T19:27:51.761044+00:00'
destination:
  file:
    name: CA-D-725-WORKBENCH_BACKEND-DECISION--read-the-workbench-result-ttl-at-startup.md
    path: .anechoic_anechoic/CA-SU-14_LAYER_2_FRAMEWORK_ENGINE/CA-SU-15_FEATURE_PROGRAMMATIC/CA-SU-20_FEATURE_APPS/CA-SU-43_APP_WORKBENCH/CA-SU-45_FEATURE_WORKBENCH_BACKEND/07_delivery
---
## Summary

Read the Workbench result TTL at startup

## Claim scope

Workbench Backend startup configuration.

## Claim

### Prose Claim

Read `workbench.result_ttl_seconds` from `.anechoic_runtime/anechoic_runtime_settings.toml` at startup. Use 3,600 seconds if the setting is absent. Reject an unreadable or invalid settings file and a TTL that is not a positive integer.
