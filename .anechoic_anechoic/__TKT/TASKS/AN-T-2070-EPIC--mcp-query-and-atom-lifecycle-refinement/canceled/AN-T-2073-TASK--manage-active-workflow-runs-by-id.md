---
atom_family: TKT
atom_id: AN-T-2073
structure:
  container:
    atom: AN-T-2070
  priority: 2
context:
  template: task
state:
  status: "canceled"
  version: 1
  updated_at: "2026-11-20T19:56:14.733479+00:00"
---
## Summary

Manage active Workflow Runs by ID

## Work

1. Update RMEDO for active Run discovery, session ownership, cross-session continuation, and input correction.
2. Review and fix RMEDO against the linked Code Synopses and the Epic decision record.
3. Implement the reviewed RMEDO and verify session and Project listings, operation by Run ID, and retention of valid fields. Use the existing Atom ID and Version comments to identify the modules that implement the affected RMEDO and refresh their pins.

## Implementation entry points

- `LAYER_2_FRAMEWORK_ENGINE/FEATURE_PROGRAMMATIC/FEATURE_MCP/registry_lifecycle_provider.py`
- `LAYER_2_FRAMEWORK_ENGINE/FEATURE_PROGRAMMATIC/FEATURE_MCP/direct_gateway.py`
- `LAYER_2_FRAMEWORK_ENGINE/FEATURE_PROGRAMMATIC/FEATURE_MCP/tool_registry_runtime.py`
