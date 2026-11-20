---
identity:
  atom_id: CA-C-741
  ref_id: CA-C-741
context:
  role: concern
  form: implementation_discrepancy
  concern:
    priority: Medium
  container:
    scope_unit: CA-SU-46
  tier: 3
  topics:
    main_subject: PROJECT STRUCTURE//ANECHOIC <+ Aspects <+ Engineering <+ Delivery
      <+ Packaging
relations:
  CONCERN_ABOUT:
  - CA-D-674
  - CA-P-3053
state:
  version: 1
  status: active
  updated_at: '2026-11-13T19:36:35.200811+00:00'
destination:
  file:
    name: CA-C-741-WORKBENCH_FRONTEND-IMPLEMENTATION_DISCREPANCY--workbench-hides-source-sync-failures.md
    path: .anechoic_anechoic/CA-SU-14_LAYER_2_FRAMEWORK_ENGINE/CA-SU-15_FEATURE_PROGRAMMATIC/CA-SU-20_FEATURE_APPS/CA-SU-43_APP_WORKBENCH/CA-SU-46_FEATURE_WORKBENCH_FRONTEND/01_concern
---
## Summary

Workbench hides source sync failures

## Concern

Workbench discards failed source-status requests. After a poll fails, the status line can keep showing the previous successful sync time without indicating the failure. CA-D-674 requires the read-only status display to show an existing failure. The frontend poll is in `App.svelte` and the status display is in `SyncStatus.svelte`.
