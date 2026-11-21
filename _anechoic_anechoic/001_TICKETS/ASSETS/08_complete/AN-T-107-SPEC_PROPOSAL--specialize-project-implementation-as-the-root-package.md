---
atom_family: TKT
atom_id: AN-T-107
container:
  component: C00
priority: 2
context:
  template: Spec Proposal
state:
  status: complete
  version: 3
  updated_at: 2026-11-02 15:49:28 +0400
---
# Summary

Specialize Project Implementation as the root Package

## Decision

Implementation is a section heading, not a separate primary kind. Package/Project Implementation is specialization: Project Implementation is the root Package. Project Implementation >@(Package); Package >@(Package), >Module, >Asset and >Prompt. Module contains Code Unit, specialized as Class and Function. The root Package has no enclosing Package; each non-root Package has one immediate Package parent. The previous Implementation > Package wrapper is superseded. Existing Documentation and Resources kinds are retained separately as awaiting placement; no unapproved Package/Asset classification is inferred for them.

## State

Refine proposal and Definition Drafts only. Current source migration remains separate.
