---
atom_family: SPEC
atom_id: AN-S-3560
container:
  component: C9
tier: 5
context:
  lens: QA
state:
  status: archived
  version: 19
  updated_at: 2026-10-24 11:58:20 +0400
---
## Summary

Reject Invalid Dependency-Order Derivations

# Summary

Reject Invalid Dependency-Order Derivations

## Scope

derived non-Plan Artifact dependency orders.

## Claim

the Evaluation **must** reject one derived non-Plan Artifact dependency order **if** a relation endpoint is **not** an admitted non-Plan Artifact, one `relations.depends_on` target reference repeats, a permutation of target-list positions changes its direct-edge set **or** derived order, an edge is absent from `relations.depends_on`, `relations.derived_from` contributes an edge, **or** the direct dependency graph **contains** a cycle.

## Details

Plan blocking **must** be checked separately under CA-E-504-CORE_META_MODEL-EVAL_CASE--validate-plan-blocking-and-parallel-readiness; a Plan `BLOCKS` fact **must not** fail merely because it is absent from `relations.depends_on`.
