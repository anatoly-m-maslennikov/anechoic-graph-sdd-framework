---
atom_family: TKT
atom_id: AN-T-2210
container:
  atom: AN-T-2070
priority: 2
context:
  template: task
state:
  status: done
  version: 1
  updated_at: '2026-11-12T16:36:43.923478+00:00'
---
## Summary

Return saved query links or an explicit unavailable reason

## Work

1. Update RMEDO for saved-query and saved View link responses.
2. Review and fix RMEDO against the linked Code Synopses and the Epic decision record.
3. Implement the reviewed RMEDO and verify configured links and null URLs with a reason when unavailable. Use the existing Atom ID and Version comments to identify the modules that implement the affected RMEDO and refresh their pins.

## Implementation entry points

- `LAYER_2_FRAMEWORK_ENGINE/FEATURE_PROGRAMMATIC/FEATURE_MCP/registry_workbench_provider.py`
- `LAYER_2_FRAMEWORK_ENGINE/FEATURE_PROGRAMMATIC/FEATURE_MCP/workbench_links.py`
- `LAYER_2_FRAMEWORK_ENGINE/FEATURE_PROGRAMMATIC/FEATURE_MCP/shared_gateway.py`
