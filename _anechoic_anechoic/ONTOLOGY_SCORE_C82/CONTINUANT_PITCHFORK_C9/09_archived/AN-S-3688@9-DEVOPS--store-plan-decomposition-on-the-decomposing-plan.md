---
atom_family: SPEC
atom_id: AN-S-3688
container:
  component: C9
tier: 3
context:
  lens: DevOps
state:
  status: archived
  version: 9
  updated_at: 2026-10-19 15:55:57 +0400
---
## Summary

Store Plan decomposition on the decomposing Plan

# Summary

Store Plan decomposition on the decomposing Plan

## Scope

direct Plan-decomposition facts declared on Plan Atom frontmatter.

## Claim

the direct fact `A IS_DECOMPOSITION_OF B` **must** be declared **only** **in** Plan `A` frontmatter as `relations.is_decomposition_of`, a collection containing the canonical Atom ID of Plan `B`.

- the collection has **`<=1`** target; omission represents **`=0`** direct targets.
- derive `B DECOMPOSES_INTO A` from that declaration; do **not** store `relations.decomposes_into` **or** an independent inverse list on `B`.
- derive recursive decomposition from the direct edges; do **not** store their transitive closure.
- directory nesting **may** represent the declared Relation but **must not** create, delete, **or** retarget it. **if** a Plan is placed inside another Plan's Directory Carrier, the declared immediate decomposition target **must** match that Plan, skipping reserved Status directories.
- placement **in** `03_plan` **or** `03_plan/001_backlog` does **not** erase an explicit decomposition Relation. a matching file **and** folder carry **`=1`** Atom, **not** a self-edge.

## Details
