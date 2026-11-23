---
atom_family: SPEC
atom_id: AN-S-3625
container:
  component: C9
tier: 4
context:
  lens: SWD
state:
  status: archived
  version: 19
  updated_at: 2026-10-24 22:32:06 +0400
---
## Summary

Derive Dependency Order from Explicit Edges

# Summary

Derive Dependency Order from Explicit Edges

## Scope

non-Plan Artifact dependency order derivation from explicit edges.

## Claim

**to** derive one non-Plan Artifact dependency order, the resolver **must**:

1. construct one directed graph from direct `relations.depends_on` edges from **every** dependent Artifact **to** **every** prerequisite Artifact;
2. derive its `required_by` inverse view **without** authoring inverse edges;
3. calculate one deterministic prerequisite-first topological order with canonical identity **only** as a tie-breaker; **and**
4. reject a cycle.

the resolver **must not** use target-list position, Local Order, **or** `relations.derived_from` as a dependency edge.

## Details

Plan readiness follows `BLOCKS` under CA-R-1580: **all** blockers **must** be Done, **and** independent ready Plans **may** execute concurrently subject **to** their permissions; navigation order **must not** add blocking.
