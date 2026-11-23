---
atom_family: SPEC
atom_id: AN-S-4706
container:
  component: C16
tier: 3
context:
  lens: DevOps
state:
  status: archived
  version: 14
  updated_at: 2026-11-02 19:46:47 +0400
---
## Summary

Encode GET_EXECUTION_CONTEXT Tool binding

# Summary

Encode GET_EXECUTION_CONTEXT Tool binding

## Scope

the GET_EXECUTION_CONTEXT capability for Tool/GET_EXECUTION_CONTEXT/Carrier.

## Claim

the GET_EXECUTION_CONTEXT Tool binding **must** be carried **in** the following TOML table **in** this Atom's Details, with JSON request **and** response Carriers.

## Details

accept a Tool name or Operations Atom ID and a context budget; return source-bound content, related Workflow Steps and Actions, applicable RMED, implementation and prompt references, and explicit context gaps.

```toml
[tool_binding]
name = "GET_EXECUTION_CONTEXT"
entrypoint = "LAYER_2_FRAMEWORK_ENGINE/FEATURE_PROGRAMMATIC/FEATURE_TOOLS/TOOL_GET_EXECUTION_CONTEXT/get_execution_context.py"
action_ids = ["CA-O-114"]
mcp_name = "get_execution_context"
```

- the MCP boundary exposes the Implementation's strict input schema. unknown fields **and** invalid selectors are explicit errors.
- return repository-relative source paths **and** SHA-256 bindings. full content is loaded **only** **when** requested.
- observation cursors bind the Run ID, saved Event frontier **and** saved status fingerprint; a cursor from another Run is invalid.
