---
identity:
  atom_id: CA-D-722
  ref_id: CA-D-722
context:
  role: delivery
  form: decision
  container:
    scope_unit: CA-SU-46
  tier: 5
  topics:
    main_subject: PROJECT STRUCTURE//ANECHOIC <+ Aspects <+ Engineering <+ Development
      <+ Architecture <+ Communication <+ Interface Contracts
    dependencies:
    - MODEL//ANECHOIC <+ Projection
relations:
  SPECIALIZES:
  - CA-D-674
state:
  version: 1
  status: active
  updated_at: '2026-11-13T19:27:01.331088+00:00'
destination:
  file:
    name: CA-D-722-WORKBENCH_FRONTEND-DECISION--send-workbench-browser-operations-through-the-project-api.md
    path: .anechoic_anechoic/CA-SU-14_LAYER_2_FRAMEWORK_ENGINE/CA-SU-15_FEATURE_PROGRAMMATIC/CA-SU-20_FEATURE_APPS/CA-SU-43_APP_WORKBENCH/CA-SU-46_FEATURE_WORKBENCH_FRONTEND/07_delivery
---
## Summary

Send Workbench browser operations through the Project API

## Claim scope

The Workbench browser transport.

## Claim

### Prose Claim

Send browser operations to the canonical `/anechoic/{project}/api/{operation}` endpoint for the selected Project. Route Workspace operations and Workspace-bound View saves through the shared `interface` operation. Return the response or surface the backend error.
