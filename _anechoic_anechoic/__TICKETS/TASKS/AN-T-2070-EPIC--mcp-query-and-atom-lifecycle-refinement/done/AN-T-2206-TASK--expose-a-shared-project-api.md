---
atom_family: TKT
atom_id: AN-T-2206
container:
  atom: AN-T-2070
priority: 2
context:
  template: task
state:
  status: done
  version: 1
  updated_at: '2026-11-12T16:36:41.683635+00:00'
---
## Summary

Expose a shared Project API

## Work

1. Update RMEDO for Project API routes, Workbench compatibility aliases, and status.
2. Review and fix RMEDO against the linked Code Synopses and the Epic decision record.
3. Implement the reviewed RMEDO and verify the same handlers through canonical and legacy paths and truthful status fields. Use the existing Atom ID and Version comments to identify the modules that implement the affected RMEDO and refresh their pins.

## Implementation entry points

- `LAYER_2_FRAMEWORK_ENGINE/FEATURE_PROGRAMMATIC/FEATURE_APPS/APP_WORKBENCH/FEATURE_WORKBENCH_BACKEND/service.py`
- `LAYER_2_FRAMEWORK_ENGINE/FEATURE_PROGRAMMATIC/FEATURE_MCP/workbench_web.py`
- `LAYER_2_FRAMEWORK_ENGINE/FEATURE_PROGRAMMATIC/FEATURE_MCP/workbench_tools.py`
- `LAYER_2_FRAMEWORK_ENGINE/FEATURE_PROGRAMMATIC/FEATURE_APPS/APP_WORKBENCH/FEATURE_WORKBENCH_FRONTEND/src/lib/transport.ts`
