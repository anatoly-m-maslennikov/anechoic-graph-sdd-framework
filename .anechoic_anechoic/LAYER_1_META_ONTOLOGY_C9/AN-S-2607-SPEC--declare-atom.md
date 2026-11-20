---
atom_family: SPEC
atom_id: AN-S-2607
structure:
  container:
    component: C9
context:
  lens: SPEC
state:
  status: active
  version: 19
  updated_at: '2026-11-20T17:25:38.351511+00:00'
---

## Summary

Declare Atom

## Claim scope

MODEL//ANECHOIC <+ Node//Artifact//Atom

## Claim

### Formal Claim

```python
from anechoic.formal_claims import declare_entity
from anechoic.model import Artifact

class Atom(Artifact):
    pass

declare_entity(
    entity_name='Atom',
    entity_class=Atom,
    entity_kind='Primary',
    identity_properties=('Header.Atom ID',),
)
```
