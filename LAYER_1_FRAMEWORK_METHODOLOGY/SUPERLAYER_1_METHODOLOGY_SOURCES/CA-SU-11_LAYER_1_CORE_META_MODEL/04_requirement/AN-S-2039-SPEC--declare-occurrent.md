---
identity:
  atom_id: AN-S-2039
context:
  container:
    component: C9
  lens: SPEC
state:
  status: active
  version: 5
  updated_at: '2026-11-20T11:17:59+00:00'
---

## Summary

Declare Occurrent

## Claim scope

MODEL//ANECHOIC <+ Occurrent

## Claim

### Formal Claim

```python
from anechoic.formal_claims import declare_entity

class Occurrent:
    pass

declare_entity(entity_name="Occurrent", entity_class=Occurrent)
```
