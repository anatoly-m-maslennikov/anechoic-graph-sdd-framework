---
atom_family: SPEC
atom_id: AN-S-3092
structure:
  container:
    component: C9
context:
  lens: SPEC
state:
  status: active
  version: 2
  updated_at: '2026-11-20T14:42:07.157939+00:00'
---

## Summary

Declare Model

## Claim scope

MODEL//ANECHOIC <+ Model

## Claim

### Formal Claim

```python
from anechoic.formal_claims import declare_entity

class Model:
    pass

declare_entity(
    entity_name='Model',
    entity_class=Model,
    entity_kind='Primary',
)
```
