---
identity:
  atom_id: AN-T-2075
context:
  container:
    atom: AN-T-2070
  tier: 3
  template: task
state:
  status: active
  version: 1
  updated_at: '2026-11-12T16:36:40.082471+00:00'
---
## Summary

Enforce Atom write safety and verify lifecycle fixes

## Work

1. Update RMEDO for same-Atom edit conflicts, selected carrier validation, Summary serialization, and retained replacement lookup.
2. Review and fix RMEDO against the linked Code Synopses and the Epic decision record.
3. Implement the reviewed RMEDO and verify conflicting Runs stop, one exact carrier read, and live promotion through the checkout fixes. Use the existing Atom ID and Version comments to identify the modules that implement the affected RMEDO and refresh their pins.

## Implementation entry points

- `LAYER_2_FRAMEWORK_ENGINE/FEATURE_PROGRAMMATIC/FEATURE_APPS/APP_WORKBENCH/FEATURE_WORKBENCH_BACKEND/service.py`
- `LAYER_2_FRAMEWORK_ENGINE/FEATURE_PROGRAMMATIC/FEATURE_TOOLS/ATOM_LIFECYCLE/placement.py`
- `LAYER_2_FRAMEWORK_ENGINE/FEATURE_PROGRAMMATIC/FEATURE_TOOLS/ATOM_LIFECYCLE/source.py`
- `LAYER_2_FRAMEWORK_ENGINE/FEATURE_PROGRAMMATIC/FEATURE_TOOLS/ATOM_LIFECYCLE/publish.py`
