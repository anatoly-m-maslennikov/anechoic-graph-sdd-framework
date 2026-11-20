---
identity:
  atom_id: AN-T-110
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

Keep Substeps as leaves

## Decision

The Operator answered No to recursive Substeps. A Substep cannot contain further Substeps. Workflow >{1..} Step >{0..} Substep is retained. Every Substep is a leaf rather than another grouping level. This resolves the further-nesting part of review gap G-03; it does not create a Substep Run kind or decide unrelated Type admission.

## State

Definition Draft preparation only. Current sources, Workflow instances and Engine implementation are unchanged.
