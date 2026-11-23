---
atom_family: SPEC
atom_id: AN-S-2712
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

Define NARROWER_THAN

## Claim

The narrower Node inherits applicable Relation and Property constraints without cloning declarations or instance facts.

```CFEL
((Node, Node/**, .**) >| Independence = Primary Node) ((NARROWER_THAN)) ((Node, Node/**, .**) >| Independence = Primary Node);
NARROWER_THAN ((HAS_INVERSE)) HAS_NARROWER
```
