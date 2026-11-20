---
identity:
  atom_id: AN-S-3094
context:
  container:
    component: C9
  lens: SPEC
state:
  status: active
  version: 2
  updated_at: '2026-11-20T14:42:07.157939+00:00'
---

## Summary

Declare eDSL

## Claim scope

MODEL//ANECHOIC <+ eDSL

## Claim

### Formal Claim

```python
from anechoic.formal_claims import declare_entity

class EDSL:
    pass

declare_entity(
    entity_name='eDSL',
    entity_class=EDSL,
    entity_kind='Primary',
)
```
