---
atom_family: SPEC
atom_id: AN-S-4211
container:
  component: C9
tier: 1
context:
  lens: DES
state:
  status: archived
  version: 2
  updated_at: 2026-11-02 00:18:22 +0400
---
## Summary

Define required_by Relation

## Claim

required_by is the inverse-derived view of depends_on; its full dependency-ordering meaning remains in CA-R-1026. No independently stored reverse fact is introduced.

### Formal claim

```text
CFEL > Relation//required_by
```
