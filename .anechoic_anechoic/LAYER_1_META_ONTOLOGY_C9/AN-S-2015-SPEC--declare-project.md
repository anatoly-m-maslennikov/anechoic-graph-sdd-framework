---
atom_family: SPEC
atom_id: AN-S-2015
structure:
  container:
    component: C9
context:
  lens: SPEC
state:
  status: active
  version: 9
  updated_at: '2026-11-20T14:42:07.157939+00:00'
---

## Summary

Declare Project

## Claim scope

MODEL//ANECHOIC <+ Node//Artifact//Component//Project

## Claim

### Formal Claim

```python
from anechoic.formal_claims import declare_entity
from anechoic.model import Component

class Project(Component):
    pass

declare_entity(
    entity_name='Project',
    entity_class=Project,
    entity_kind='Primary',
)
```
