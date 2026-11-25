---
atom_family: SPEC
atom_id: AN-S-2200
container:
  component: C9
tier: 2
context:
  lens: SPEC
state:
  status: "archived"
  version: 7
  updated_at: '2026-11-20T14:42:07.157939+00:00'
---

## Summary

Define View

## Claim scope

MODEL//ANECHOIC <+ View

## Claim

### Formal Claim

```python
from anechoic.formal_claims import declare_entity

class View:
    pass

declare_entity(
    entity_name='View',
    entity_class=View,
    entity_kind='Primary',
)
```
