---
atom_family: TKT
atom_id: AN-T-2207
container:
  atom: AN-T-2070
priority: 2
context:
  template: task
state:
  status: done
  version: 1
  updated_at: '2026-11-12T16:36:42.267477+00:00'
---
## Summary

Keep Workbench usable without browser storage

## Work

1. Update RMEDO for Workspace binding, embedded density, and storage failure.
2. Review and fix RMEDO against the linked Code Synopses and the Epic decision record.
3. Implement the reviewed RMEDO and verify stable Workspace identity, canonical Project name, and a warning with in-memory edits. Use the existing Atom ID and Version comments to identify the modules that implement the affected RMEDO and refresh their pins.

## Implementation entry points

- `LAYER_2_FRAMEWORK_ENGINE/FEATURE_PROGRAMMATIC/FEATURE_APPS/APP_WORKBENCH/FEATURE_WORKBENCH_FRONTEND/src/App.svelte`
- `LAYER_2_FRAMEWORK_ENGINE/FEATURE_PROGRAMMATIC/FEATURE_MCP/workbench_tools.py`
- `LAYER_2_FRAMEWORK_ENGINE/FEATURE_PROGRAMMATIC/FEATURE_APPS/APP_WORKBENCH/FEATURE_WORKBENCH_FRONTEND/src/lib/workspace.js`
