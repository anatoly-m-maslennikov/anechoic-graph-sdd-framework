---
identity:
  atom_id: AN-S-339
context:
  container:
    component: C9
  tier: 2
  lens: DES
state:
  status: active
  version: 26
  updated_at: 2026-11-02 00:18:22 +0400
---
## Summary

Keep Entity Identity Independent of Graph Materialization

## Claim

### Prose Claim


Entity identity while a Graph Projection is materialized, refreshed, or deleted.


materializing, refreshing, **or** deleting a Graph Projection **must not** establish, change, **or** remove Entity identity.
