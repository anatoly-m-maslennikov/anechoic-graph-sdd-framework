---
atom_family: SPEC
atom_id: AN-S-2714
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

Define classification and its written reverse

## Claim

HAS_CLASSIFICATION relates a Node to an applicable classification axis. `Node >| Axis` and `Axis |< Node` are opposite written views of the same fact. An axis is distinct from its value case.

```CFEL
(Node, Node/**, .**) >| Axis
```
