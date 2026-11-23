---
atom_family: TKT
atom_id: AN-T-106
container:
  component: C00
priority: 2
context:
  template: spec_proposal
state:
  status: archived
  version: 2
  updated_at: 2026-10-29 21:51:04 +0400
---
## Summary

Specialize Project as the root Scope Unit

# Summary

Specialize Project as the root Scope Unit

## Decision

Scope Unit/Project is specialization. Project is the single root Scope Unit, without a parent Scope Unit. Project >@(Scope Unit); Scope Unit >@(Scope Unit), >@(Atom), >@(Projection) are structural containment. Project is not a separate sibling kind which merely contains all Scope Units. Scope Unit properties therefore apply to Project through specialization, with the explicit root-parent exception. Project Goal Operator ownership remains unchanged.

## State

Refine proposal and Definition Drafts only. Current source migration remains separate.
