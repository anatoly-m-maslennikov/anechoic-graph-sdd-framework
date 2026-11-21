---
atom_family: SPEC
atom_id: AN-S-3113
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

Declare Contract

## Claim scope

MODEL//ANECHOIC <+ Node//Artifact//Atom//Spec Atom//Contract

## Claim

### Formal Claim

```python
from anechoic.formal_claims import declare_entity
from anechoic.model import SpecAtom

class Contract(SpecAtom):
    pass

declare_entity(
    entity_name='Contract',
    entity_class=Contract,
    entity_kind='Primary',
)
```
