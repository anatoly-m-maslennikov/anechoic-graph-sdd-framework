---
atom_family: TKT
atom_id: AN-T-104
container:
  component: C00
priority: 2
context:
  template: spec_proposal
state:
  status: archived
  version: 1
  updated_at: 2026-10-28 20:51:13 +0400
---
## Summary

Require Code Units inside Modules

# Summary

Require Code Units inside Modules

## Decision

Module is a file-level Code component. Code Unit is declared inside Module, with Class and Function as narrower kinds. A Code Unit has no independent declaration directly under Code. Continuant classification can reference the same kind without permitting independent existence.

## State

This resolves the earlier unnecessary Module-versus-direct-Code question. It does not settle the separate alternatives for a Module contained by Code or Package. Draft refinement only.
