---
identity:
  atom_id: AN-S-2596
context:
  container:
    component: C9
  lens: SPEC
state:
  status: active
  version: 7
  updated_at: '2026-11-20T14:42:07.157939+00:00'
---

## Summary

Declare Package

## Claim scope

MODEL//ANECHOIC <+ Node//Artifact//Package

## Claim

### Formal Claim

```python
from anechoic.formal_claims import declare_entity
from anechoic.model import Artifact

class Package(Artifact):
    pass

declare_entity(
    entity_name='Package',
    entity_class=Package,
    entity_kind='Primary',
)
```
