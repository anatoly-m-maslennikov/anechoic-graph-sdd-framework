---
atom_family: SPEC
atom_id: AN-S-2715
container:
  component: C9
tier: 3
context:
  lens: DES
state:
  status: archived
  version: 2
  updated_at: 2026-11-02 00:18:22 +0400
---
## Summary

Define composition and its inverse

## Claim

IS_CONTAINED_BY relates a contained Node to its immediate Container. Containment does not imply narrowing or inheritance.

```CFEL
(Node, Node/**, .**) ((IS_CONTAINED_BY)) ((Node, Node/**, .**) >| Container = yes);
IS_CONTAINED_BY ((HAS_INVERSE)) CONTAINS
```
