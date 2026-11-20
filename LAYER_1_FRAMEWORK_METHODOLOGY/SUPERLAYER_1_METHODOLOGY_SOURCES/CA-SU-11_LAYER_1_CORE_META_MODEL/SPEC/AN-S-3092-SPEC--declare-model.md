---
identity:
  atom_id: AN-S-3092
context:
  container:
    component: C9
  lens: SPEC
state:
  status: active
  version: 1
  updated_at: '2026-11-20T11:17:59+00:00'
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

declare_entity(entity_name="Model", entity_class=Model)
```
