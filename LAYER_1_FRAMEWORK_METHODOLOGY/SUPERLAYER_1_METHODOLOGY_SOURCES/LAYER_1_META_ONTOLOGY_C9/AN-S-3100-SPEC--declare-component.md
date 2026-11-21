---
atom_family: SPEC
atom_id: AN-S-3100
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

Declare Component

## Claim scope

MODEL//ANECHOIC <+ Node//Artifact//Component

## Claim

### Formal Claim

```python
from anechoic.formal_claims import declare_entity
from anechoic.model import Artifact

class Component(Artifact):
    pass

declare_entity(
    entity_name='Component',
    entity_class=Component,
    entity_kind='Primary',
)
```
