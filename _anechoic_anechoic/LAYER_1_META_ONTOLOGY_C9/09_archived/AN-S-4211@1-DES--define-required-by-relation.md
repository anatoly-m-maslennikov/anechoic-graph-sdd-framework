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
  version: 1
  updated_at: 2026-10-29 17:12:04 +0400
---
## Summary

Define required_by Relation

## Claim

required_by is the inverse-derived view of depends_on; its full dependency-ordering meaning remains in CA-R-1026. No independently stored reverse fact is introduced.

### Formal claim

```text
Entity/Graph Syntax > Relation//required_by
```
