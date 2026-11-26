---
atom_family: SPEC
atom_id: AN-S-2697
container:
  component: C9
tier: 2
context:
  lens: SPEC
state:
  status: "archived"
  version: 18
  updated_at: '2026-11-20T14:42:07.157939+00:00'
---

## Summary

Define Relation

## Claim scope

MODEL//ANECHOIC <+ Graph/Relation

## Claim

### Formal Claim

```python
from anechoic.formal_claims import declare_entity

class Relation:
    pass

declare_entity(
    entity_name='Relation',
    entity_class=Relation,
    entity_kind='Primary',
)
```
