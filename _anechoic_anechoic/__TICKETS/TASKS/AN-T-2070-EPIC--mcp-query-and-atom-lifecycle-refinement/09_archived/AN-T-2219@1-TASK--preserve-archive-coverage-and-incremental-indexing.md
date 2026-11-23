---
atom_family: TKT
atom_id: AN-T-2219
container:
  atom: AN-T-2070
priority: 2
context:
  template: task
state:
  status: archived
  version: 1
  updated_at: '2026-11-12T16:36:41.315751+00:00'
---
## Summary

Preserve Archive coverage and incremental indexing

## Work

1. Update RMEDO for reread coverage, incremental refresh, and background audit preparation.
2. Review and fix RMEDO against the linked Code Synopses and the Epic decision record.
3. Implement the reviewed RMEDO and verify selected Archives remain queryable, ordinary refresh stays targeted, and performance guards pass. Use the existing Atom ID and Version comments to identify the modules that implement the affected RMEDO and refresh their pins.

## Implementation entry points

- `LAYER_2_FRAMEWORK_ENGINE/FEATURE_PROGRAMMATIC/FEATURE_APPS/APP_WORKBENCH/FEATURE_WORKBENCH_BACKEND/service.py`
- `LAYER_2_FRAMEWORK_ENGINE/FEATURE_PROGRAMMATIC/FEATURE_APPS/APP_WORKBENCH/FEATURE_WORKBENCH_BACKEND/source_reader.py`
- `LAYER_2_FRAMEWORK_ENGINE/FEATURE_PROGRAMMATIC/FEATURE_MCP/workbench_tools.py`
