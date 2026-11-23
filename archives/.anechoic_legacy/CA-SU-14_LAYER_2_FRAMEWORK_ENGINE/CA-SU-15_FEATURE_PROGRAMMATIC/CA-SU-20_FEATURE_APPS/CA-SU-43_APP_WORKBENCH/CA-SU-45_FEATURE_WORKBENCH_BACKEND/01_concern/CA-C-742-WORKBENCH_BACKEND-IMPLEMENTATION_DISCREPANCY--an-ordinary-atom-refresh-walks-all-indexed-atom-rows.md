---
identity:
  atom_id: CA-C-742
  ref_id: CA-C-742
context:
  role: concern
  form: implementation_discrepancy
  concern:
    priority: Medium
  container:
    scope_unit: CA-SU-45
  tier: 3
  topics:
    main_subject: PROJECT STRUCTURE//ANECHOIC <+ Aspects <+ Engineering <+ Operation
      <+ Data Handling <+ Indexing
relations:
  CONCERN_ABOUT:
  - CA-M-465
  - CA-P-3053
state:
  version: 1
  status: active
  updated_at: '2026-11-13T19:36:54.876137+00:00'
destination:
  file:
    name: CA-C-742-WORKBENCH_BACKEND-IMPLEMENTATION_DISCREPANCY--an-ordinary-atom-refresh-walks-all-indexed-atom-rows.md
    path: .anechoic_anechoic/CA-SU-14_LAYER_2_FRAMEWORK_ENGINE/CA-SU-15_FEATURE_PROGRAMMATIC/CA-SU-20_FEATURE_APPS/CA-SU-43_APP_WORKBENCH/CA-SU-45_FEATURE_WORKBENCH_BACKEND/01_concern
---
## Summary

An ordinary Atom refresh walks all indexed Atom rows

## Concern

CA-M-465 requires ordinary Atom changes to avoid a full inventory walk. `service_refresh.py` scans the captured Atom rows for active IDs and rebuilds the source-path set even for a single Atom change. Verify that an ordinary delta updates the affected paths and Archive summary inputs only.
