---
atom_family: SPEC
atom_id: AN-S-3097
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

Declare Spec Atom

## Claim scope

MODEL//ANECHOIC <+ Node//Artifact//Atom//Spec Atom

## Claim

### Formal Claim

```python
from anechoic.formal_claims import declare_entity
from anechoic.model import Atom

class SpecAtom(Atom):
    pass

declare_entity(
    entity_name='Spec Atom',
    entity_class=SpecAtom,
    entity_kind='Primary',
)
```
