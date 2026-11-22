---
atom_family: SPEC
atom_id: AN-S-3104
container:
  component: C9
tier: 2
context:
  lens: SPEC
state:
  status: active
  version: 2
  updated_at: '2026-11-20T14:42:07.157939+00:00'
---

## Summary

Declare Unit

## Claim scope

MODEL//ANECHOIC <+ Module/Unit

## Claim

### Formal Claim

```python
from anechoic.formal_claims import declare_entity

class Unit:
    pass

declare_entity(
    entity_name='Unit',
    entity_class=Unit,
    entity_kind='Primary',
)
```
