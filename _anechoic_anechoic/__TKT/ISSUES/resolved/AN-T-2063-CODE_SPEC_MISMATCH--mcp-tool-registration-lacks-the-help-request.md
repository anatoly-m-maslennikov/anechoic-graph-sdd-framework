---
atom_family: TKT
atom_id: AN-T-2063
structure:
  container:
    component: C14
  priority: 2
context:
  template: Code-Spec Mismatch
state:
  status: "resolved"
  version: 2
  updated_at: "2026-11-21T00:55:34.283850+00:00"
---
## Summary

MCP Tool registration lacks the help request

## Claim

### Prose Claim

In the ANECHOIC working tree based on `c0b983cb27`, `LAYER_2_FRAMEWORK_ENGINE/FEATURE_PROGRAMMATIC/FEATURE_MCP/shared_tool_contract.py`, `public_tool`, and `LAYER_2_FRAMEWORK_ENGINE/FEATURE_PROGRAMMATIC/FEATURE_MCP/tool_registry_runtime.py`, `ActiveToolRegistry.call`, expose and validate normal Tool arguments. The generated Tool registry and dispatch have no separate `help: true` request. CA-R-3065@1, CA-M-548@1 and CA-D-714@1 require Tool help before normal business validation. An ordinary MCP Tool request with help is rejected by the current schema.
