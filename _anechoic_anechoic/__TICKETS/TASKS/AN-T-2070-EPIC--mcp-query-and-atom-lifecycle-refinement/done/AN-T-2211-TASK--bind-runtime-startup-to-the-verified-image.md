---
atom_family: TKT
atom_id: AN-T-2211
container:
  atom: AN-T-2070
priority: 2
context:
  template: task
state:
  status: done
  version: 1
  updated_at: '2026-11-12T16:36:36.150716+00:00'
---
## Summary

Bind runtime startup to the verified image

## Work

1. Update RMEDO for image identity and build and startup timeouts.
2. Review and fix RMEDO against the linked Code Synopses and the Epic decision record.
3. Implement the reviewed RMEDO and verify checkout-change refusal and enforcement of the configured timeouts. Use the existing Atom ID and Version comments to identify the modules that implement the affected RMEDO and refresh their pins.

## Implementation entry points

- `LAYER_2_FRAMEWORK_ENGINE/FEATURE_PROGRAMMATIC/FEATURE_MCP/docker/project_mcp_backend.py`
- `LAYER_2_FRAMEWORK_ENGINE/FEATURE_PROGRAMMATIC/FEATURE_MCP/docker/project-mcp.compose.yaml`
- `LAYER_2_FRAMEWORK_ENGINE/FEATURE_PROGRAMMATIC/FEATURE_MCP/docker/runtime.py`
- `LAYER_2_FRAMEWORK_ENGINE/FEATURE_PROGRAMMATIC/FEATURE_MCP/docker/start_mcp.py`
