---
atom_family: SPEC
atom_id: AN-S-4708
container:
  component: C16
tier: 3
context:
  lens: DevOps
state:
  status: archived
  version: 3
  updated_at: 2026-10-23 03:14:50 +0400
---
## Summary

Encode RESUME_EXECUTION_CONTEXT Tool binding

# Summary

Encode RESUME_EXECUTION_CONTEXT Tool binding

## Scope

the RESUME_EXECUTION_CONTEXT capability for Tool/RESUME_EXECUTION_CONTEXT/Carrier.

## Claim

the RESUME_EXECUTION_CONTEXT Tool binding **must** be carried **in** the following TOML table **in** this Atom's Details, with JSON request **and** response Carriers.

## Details

accept a supported Run ID; return original request, frozen selection and criteria bindings, pending check or fix work, saved handoffs, current-source observations, and recording blockers.

```toml
[tool_binding]
name = "RESUME_EXECUTION_CONTEXT"
entrypoint = "102_FRAMEWORK_ENGINE/201_PROGRAMMATIC/201_TOOLS/RESUME_EXECUTION_CONTEXT/resume_execution_context.py"
action_ids = ["CA-O-116"]
mcp_name = "resume_execution_context"
```

- the MCP boundary exposes the Implementation's strict input schema. unknown fields **and** invalid selectors are explicit errors.
- return repository-relative source paths **and** SHA-256 bindings. full content is loaded **only** **when** requested.
- observation cursors bind the Run ID, saved Event frontier **and** saved status fingerprint; a cursor from another Run is invalid.
