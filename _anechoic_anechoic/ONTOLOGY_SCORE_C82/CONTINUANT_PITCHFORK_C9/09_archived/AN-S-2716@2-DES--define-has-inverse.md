---
atom_family: SPEC
atom_id: AN-S-2716
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

Define HAS_INVERSE

## Claim

HAS_INVERSE links a direct Relation to its derived inverse. The inverse swaps the direct Relation's Host and Target. Its links are derived from the direct links and are not authored separately.

```CFEL
Relation// ((HAS_INVERSE)) Relation//
```
