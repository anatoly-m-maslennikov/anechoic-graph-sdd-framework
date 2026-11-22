---
atom_family: SPEC
atom_id: AN-S-2039
container:
  component: C9
tier: 2
context:
  lens: SPEC
state:
  status: active
  version: 6
  updated_at: '2026-11-20T14:42:07.157939+00:00'
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

declare_entity(
    entity_name='Occurrent',
    entity_class=Occurrent,
    entity_kind='Primary',
)
```
