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
  version: 1
  updated_at: 2026-11-03 23:17:14 +0400
---
## Summary

Expand indexed Relation references with complete cycle-safe results

## Claim scope

Expansion of an unambiguous seed reference through indexed registered Relation Types.

## Claim

### Prose Claim

Relation expansion **must**:

- accept one unambiguous seed reference and one or more registered Relation Types.
- include the seed and every reachable typed reference exactly once across all selected Relation Types and directions.
- terminate on cycles.
- return typed references, not fetched Atom or Scope Unit copies.
- use only indexed relation facts; it **must not** infer links from prose or interpret Formal Claims as graph declarations.
- resolve a declared inverse from its corresponding direct indexed fact once, in the requested direction, without creating another source relation or duplicate traversal fact.

