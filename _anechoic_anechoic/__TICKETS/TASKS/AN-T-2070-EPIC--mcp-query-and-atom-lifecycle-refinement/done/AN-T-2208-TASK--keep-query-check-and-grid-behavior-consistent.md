---
atom_family: TKT
atom_id: AN-T-2208
container:
  atom: AN-T-2070
priority: 2
context:
  template: task
state:
  status: done
  version: 1
  updated_at: '2026-11-12T16:36:42.539116+00:00'
---
## Summary

Keep query Check and grid behavior consistent

## Work

1. Update RMEDO for Check feedback and single-query grid behavior.
2. Review and fix RMEDO against the linked Code Synopses and the Epic decision record.
3. Implement the reviewed RMEDO and verify the three Check states and one-query grid acceptance. Use the existing Atom ID and Version comments to identify the modules that implement the affected RMEDO and refresh their pins.

## Implementation entry points

- `LAYER_2_FRAMEWORK_ENGINE/FEATURE_PROGRAMMATIC/FEATURE_APPS/APP_IWE_CONSOLE/FEATURE_IWE_CONSOLE_FRONTEND/src/App.svelte`
- `LAYER_2_FRAMEWORK_ENGINE/FEATURE_PROGRAMMATIC/FEATURE_APPS/APP_IWE_CONSOLE/FEATURE_IWE_CONSOLE_FRONTEND/src/lib/ResultsTable.svelte`
- `LAYER_2_FRAMEWORK_ENGINE/FEATURE_PROGRAMMATIC/FEATURE_APPS/APP_IWE_CONSOLE/FEATURE_IWE_CONSOLE_BACKEND/query_admission.py`
