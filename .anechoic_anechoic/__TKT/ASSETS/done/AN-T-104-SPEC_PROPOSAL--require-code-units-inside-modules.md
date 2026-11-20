---
identity:
  atom_id: AN-T-104
context:
  container:
    component: C00
  tier: 3
  template: Spec Proposal
state:
  status: done
  version: 3
  updated_at: 2026-11-02 15:49:28 +0400
---
# Summary

Require Code Units inside Modules

## Decision

Module is a file-level Code component. Code Unit is declared inside Module, with Class and Function as narrower kinds. A Code Unit has no independent declaration directly under Code. Continuant classification can reference the same kind without permitting independent existence.

## State

This resolves the earlier unnecessary Module-versus-direct-Code question. It does not settle the separate alternatives for a Module contained by Code or Package. Draft refinement only.
