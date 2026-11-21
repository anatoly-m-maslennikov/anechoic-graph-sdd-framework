---
atom_family: SPEC
atom_id: AN-S-2066
structure:
  container:
    component: C9
context:
  lens: SPEC
state:
  status: archived
  version: 4
  updated_at: '2026-11-20T11:17:59+00:00'
---

## Summary

Declare Atom.Header.Ref ID

## Claim scope

MODEL//ANECHOIC <+ Node//Artifact//Atom.Ref ID

## Claim

### Formal Claim

```python
from anechoic.formal_claims import declare_entity

declare_entity(
    entity_name="Ref ID",
    relation_name="IS_PROPERTY_OF",
    base_path="Node//Artifact//Atom",
    value_format=str,
    value_cardinality=1,
)
```
