---
atom_family: SPEC
atom_id: AN-S-1830
container:
  component: C58
tier: 3
context:
  template: action
  lens: DOM/MTD
state:
  status: active
  version: 1
  updated_at: 2026-11-11 14:05:36 +0400
---
## Summary

Read Workflow intake input

## Claim scope

One bound Workflow Run and its MCP intake dictionary.

## Claim

### Inputs

The bound Project, Workflow Run, request and MCP intake dictionary.

### Fixed parameters

None.

### Effect

At MCP entry, read the dictionary bound to the Project Run and invocation; when called by a Workflow, read its actual caller-bound dictionary, never the parent MCP query. Validate only that binding and the dictionary envelope. Do not infer, supplement, validate fields or mutate a carrier.

### Outputs

Return the dictionary unchanged. Return an explicit failure if the binding or dictionary envelope is invalid.
