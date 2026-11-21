---
atom_family: TKT
atom_id: AN-T-1685
container:
  component: C00
priority: 2
context:
  template: Spec Proposal
state:
  status: complete
  version: 4
  updated_at: 2026-11-02 15:49:28 +0400
---
## Summary

Define the main Relation once and reference its derived counterpart

## Proposal

Define only the main direction in full. The derived counterpart has only its name and a short reference to the main direction. The counterpart reuses the main direction's definition through that short reference. Do not duplicate meaning, constraints or a complete second Definition. This is the DRY reason for deriving the counterpart.

## Status

Accepted by the Operator on 2026-10-29 15:24:34 +0400. [P2696](../../03_plan/CA-P-2694-EPIC--entity-graph-refactor-stage-4-polishing/020_done/02-CA-P-2696-TASK--establish-one-defining-requirement-per-model-entity.md) owns Draft adoption and the remaining Definition ownership corrections. The Epic remains Active.
