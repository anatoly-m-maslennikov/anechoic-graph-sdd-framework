---
atom_family: SPEC
atom_id: AN-S-1999
structure:
  container:
    component: C9
context:
  lens: SPEC
state:
  status: active
  version: 19
  updated_at: '2026-11-20T14:42:07.157939+00:00'
---

## Summary

Define Entity/Carrier

## Claim scope

MODEL//ANECHOIC <+ Carrier

## Claim

### Formal Claim

```python
from anechoic.formal_claims import declare_entity

class Carrier:
    pass

declare_entity(
    entity_name='Carrier',
    entity_class=Carrier,
    entity_kind='Primary',
)
```
