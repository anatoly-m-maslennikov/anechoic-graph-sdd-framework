---
atom_family: SPEC
atom_id: AN-S-2789
structure:
  container:
    component: C9
context:
  lens: SPEC
state:
  status: active
  version: 10
  updated_at: '2026-11-20T14:42:07.157939+00:00'
---

## Summary

Define Cardinality

## Claim scope

MODEL//ANECHOIC <+ eDSL/Cardinality

## Claim

### Formal Claim

```python
from anechoic.formal_claims import declare_entity

class Cardinality:
    pass

declare_entity(
    entity_name='Cardinality',
    entity_class=Cardinality,
    entity_kind='Primary',
)
```
