---
atom_family: TKT
atom_id: AN-T-2041
container:
  component: C14
priority: 2
context:
  template: Code-Spec Mismatch
state:
  status: in_queue
  version: 1
  updated_at: '2026-11-12T12:49:04.420687+00:00'
---
## Summary

MCP schema errors bypass lifecycle field correction

## Claim

### Prose Claim

In the ANECHOIC working tree based on `c0b983cb27`, `LAYER_2_FRAMEWORK_ENGINE/FEATURE_PROGRAMMATIC/FEATURE_MCP/tool_registry_runtime.py`, `ActiveToolRegistry.call`, validates the outer schema before invoking the lifecycle provider. `LAYER_2_FRAMEWORK_ENGINE/FEATURE_PROGRAMMATIC/FEATURE_MCP/direct_gateway.py`, `_input_rejection`, returns generic `tool_input_invalid` for an unknown field or an invalid outer field type. Those requests never reach the pending-input path in `LAYER_2_FRAMEWORK_ENGINE/FEATURE_PROGRAMMATIC/FEATURE_MCP/registry_lifecycle_provider.py`. CA-R-1105@31 and CA-M-167@26 require field-level errors and correction input in the MCP response. Business field correction reaches that path, while outer schema rejection does not.
