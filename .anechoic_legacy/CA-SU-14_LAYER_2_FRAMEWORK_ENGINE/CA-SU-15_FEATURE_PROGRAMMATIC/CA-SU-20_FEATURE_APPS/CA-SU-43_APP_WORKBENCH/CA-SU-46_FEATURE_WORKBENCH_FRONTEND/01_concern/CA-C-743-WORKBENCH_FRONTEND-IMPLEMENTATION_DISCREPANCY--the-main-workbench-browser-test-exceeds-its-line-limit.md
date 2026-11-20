---
identity:
  atom_id: CA-C-743
  ref_id: CA-C-743
context:
  role: concern
  form: implementation_discrepancy
  concern:
    priority: Medium
  container:
    scope_unit: CA-SU-46
  tier: 3
  topics:
    main_subject: PROJECT STRUCTURE//ANECHOIC <+ Aspects <+ Engineering <+ Quality
      <+ Verification
relations:
  CONCERN_ABOUT:
  - CA-M-467
  - CA-P-3053
state:
  version: 1
  status: active
  updated_at: '2026-11-13T19:36:58.421506+00:00'
destination:
  file:
    name: CA-C-743-WORKBENCH_FRONTEND-IMPLEMENTATION_DISCREPANCY--the-main-workbench-browser-test-exceeds-its-line-limit.md
    path: .anechoic_anechoic/CA-SU-14_LAYER_2_FRAMEWORK_ENGINE/CA-SU-15_FEATURE_PROGRAMMATIC/CA-SU-20_FEATURE_APPS/CA-SU-43_APP_WORKBENCH/CA-SU-46_FEATURE_WORKBENCH_FRONTEND/01_concern
---
## Summary

The main Workbench browser test exceeds its line limit

## Concern

`tests/workbench.e2e.spec.ts` is 518 lines. CA-M-467 sets a mandatory 500-line limit for a frontend file. Split the test along existing scenarios and keep its coverage.
