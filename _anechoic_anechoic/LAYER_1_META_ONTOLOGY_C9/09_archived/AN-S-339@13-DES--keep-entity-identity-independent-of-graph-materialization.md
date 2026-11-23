---
atom_family: SPEC
atom_id: AN-S-339
container:
  component: C9
tier: 1
context:
  lens: DES
state:
  status: archived
  version: 13
  updated_at: 2026-10-19 15:52:59 +0400
---
## Summary

Keep Entity Identity Independent of Graph Materialization

# Summary

Keep Entity Identity Independent of Graph Materialization

## Scope

Entity identity while a Graph Projection is materialized, refreshed, or deleted.

## Claim

materializing, refreshing, **or** deleting a Graph Projection **must not** establish, change, **or** remove Entity identity.

## Details
