---
atom_family: TKT
atom_id: AN-T-110
container:
  component: C00
priority: 2
context:
  template: spec_proposal
state:
  status: archived
  version: 1
  updated_at: 2026-10-28 22:56:37 +0400
---
## Summary

Keep Substeps as leaves

# Summary

Keep Substeps as leaves

## Decision

The Operator answered No to recursive Substeps. A Substep cannot contain further Substeps. Workflow >{1..} Step >{0..} Substep is retained. Every Substep is a leaf rather than another grouping level. This resolves the further-nesting part of review gap G-03; it does not create a Substep Run kind or decide unrelated Type admission.

## State

Definition Draft preparation only. Current sources, Workflow instances and Engine implementation are unchanged.
