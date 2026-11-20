---
atom_family: SPEC
atom_id: AN-S-3112
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

Declare Component Purpose

## Claim scope

MODEL//ANECHOIC <+ Node//Artifact//Atom//Spec Atom//Purpose//Component Purpose

## Claim

### Formal Claim

```python
from anechoic.formal_claims import declare_entity
from anechoic.model import Purpose

class ComponentPurpose(Purpose):
    pass

declare_entity(
    entity_name='Component Purpose',
    entity_class=ComponentPurpose,
    entity_kind='Primary',
)
```
