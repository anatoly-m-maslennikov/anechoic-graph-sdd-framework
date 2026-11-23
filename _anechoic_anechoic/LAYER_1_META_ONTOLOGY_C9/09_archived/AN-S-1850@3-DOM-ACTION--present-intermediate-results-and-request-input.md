---
atom_family: SPEC
atom_id: AN-S-1850
container:
  component: C9
tier: 3
context:
  template: action
  lens: DES/DOM
state:
  status: archived
  version: 3
  updated_at: 2026-11-11 14:29:18 +0400
---
## Summary

Present intermediate results and request input

## Claim scope

One bound Workflow Run that needs additional input before its current Step can continue.

## Claim

### Inputs

The bound Project, Workflow Run and current Step; intermediate results; separate warnings; and a `requested_input` dictionary. It may carry checker field entries or a broader request for additional information.

### Fixed parameters

None.

### Effect

Wait for a correction dictionary bound to the same Project, Run and Step. The caller may cancel while waiting; cancellation does not interrupt an Action. Return the missing or invalid fields. A later MCP request for the same Tool in the same Project and client session can supply only those fields. It may also supply corrections to other inputs. Merge the supplied fields into the retained input and validate the resulting request before any effect.

### Outputs

While waiting, return intermediate results, warnings and `requested_input`; after a valid resumed call, return the correction dictionary and warnings unchanged. Report an explicit failure if the resumed binding or dictionary envelope is invalid.
