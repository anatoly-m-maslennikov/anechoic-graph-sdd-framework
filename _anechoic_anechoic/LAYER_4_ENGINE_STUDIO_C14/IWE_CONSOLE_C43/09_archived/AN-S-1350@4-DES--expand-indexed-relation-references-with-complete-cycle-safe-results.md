---
atom_family: SPEC
atom_id: AN-S-1350
container:
  component: C43
tier: 3
context:
  lens: DES
state:
  status: archived
  version: 4
  updated_at: 2026-11-09 00:09:26 +0400
---
## Summary

Expand indexed Relation references with complete cycle-safe results

## Claim

### Prose Claim

Relation expansion **must**:

- accept one unambiguous seed reference and one or more registered Relation Types.
- include the seed and every reachable typed reference exactly once across all selected Relation Types and directions.
- terminate on cycles.
- return references, not fetched Atom or Scope Unit copies.
- use only indexed Relation facts; it **must not** infer links from prose or interpret Formal Claims as graph declarations.
- resolve each declared derived counterpart from its direct source fact without creating a second direct fact or traversing an inverse twice.
- reflect the applicable source and Declaration state after its query Projection is refreshed.
- use only `atoms` and `scope_units` as Relation-expansion source tables. The separate technical `change_log` table records watcher observations and is not a graph vertex, edge, Atom or Scope Unit source.

