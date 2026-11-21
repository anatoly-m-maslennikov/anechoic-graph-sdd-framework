---
atom_family: TKT
atom_id: AN-T-2205
container:
  atom: AN-T-2070
priority: 2
context:
  template: task
state:
  status: done
  version: 1
  updated_at: '2026-11-12T16:36:42.804097+00:00'
---
## Summary

Publish Tool help through MCP discovery

## Work

1. Update RMEDO for Tool descriptions and argument schemas.
2. Review and fix RMEDO against the linked Code Synopses and the Epic decision record.
3. Implement the reviewed RMEDO and verify standard tools/list discovery. Use the existing Atom ID and Version comments to identify the modules that implement the affected RMEDO and refresh their pins.

## Implementation entry points

- `LAYER_2_FRAMEWORK_ENGINE/FEATURE_PROGRAMMATIC/FEATURE_MCP/shared_tool_contract.py`
- `LAYER_2_FRAMEWORK_ENGINE/FEATURE_PROGRAMMATIC/FEATURE_MCP/tool_registry_runtime.py`
- `LAYER_2_FRAMEWORK_ENGINE/FEATURE_PROGRAMMATIC/FEATURE_MCP/shared_gateway.py`
