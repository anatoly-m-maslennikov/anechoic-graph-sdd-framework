---
atom_family: SPEC
atom_id: AN-S-2711
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

Define Property bearing and its inverse

## Claim

IS_PROPERTY_OF directs a Property to exactly one immediate bearer. HAS_PROPERTY is its derived inverse. The bearer relation is acyclic. `Bearer.Property` addresses the Property.

```CFEL
((Node, Node/**, .**) >| Independence = Property) {:1}((IS_PROPERTY_OF)) (Node, Node/**, .**);
IS_PROPERTY_OF ((HAS_INVERSE)) HAS_PROPERTY
```
