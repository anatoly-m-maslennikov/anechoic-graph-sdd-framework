---
atom_family: SPEC
atom_id: AN-S-339
container:
  component: C9
tier: 2
context:
  lens: DES
state:
  status: "archived"
  version: 26
  updated_at: "2026-11-25T19:40:37.190735+00:00"
---
## Summary

Keep Entity Identity Independent of Graph Materialization

## Claim

### Prose Claim


Entity identity while a Graph Projection is materialized, refreshed, or deleted.


materializing, refreshing, **or** deleting a Graph Projection **must not** establish, change, **or** remove Entity identity.
