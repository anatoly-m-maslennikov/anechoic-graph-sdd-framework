---
atom_family: SPEC
atom_id: AN-S-2680
container:
  component: C9
tier: 1
context:
  lens: DES
state:
  status: archived
  version: 34
  updated_at: 2026-10-30 16:24:49 +0400
---
## Summary

Register derived_from relation

## Claim scope

direct derivation relations between exact represented content versions.

## Claim

DERIVED_FROM means the directed Relation from a derived represented content version to an exact source content version used to derive it. Version references identify the relevant states; this does not introduce a Revision entity.

### Formal claim

```text
Entity/Graph Syntax <+ Relation//DERIVED_FROM
```
