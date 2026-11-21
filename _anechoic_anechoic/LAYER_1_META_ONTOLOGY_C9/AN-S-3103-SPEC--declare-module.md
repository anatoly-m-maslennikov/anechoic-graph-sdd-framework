---
atom_family: SPEC
atom_id: AN-S-3103
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

Declare Module

## Claim scope

MODEL//ANECHOIC <+ Package/Module

## Claim

### Formal Claim

```python
from anechoic.formal_claims import declare_entity

class Module:
    pass

declare_entity(
    entity_name='Module',
    entity_class=Module,
    entity_kind='Primary',
)
```
