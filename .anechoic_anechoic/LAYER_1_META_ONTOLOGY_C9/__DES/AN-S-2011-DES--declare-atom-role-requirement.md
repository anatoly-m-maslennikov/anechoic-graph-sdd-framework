---
atom_family: SPEC
atom_id: AN-S-2011
structure:
  container:
    component: C9
  tier: 3
context:
  lens: DES
state:
  status: active
  version: 7
  updated_at: '2026-11-12T12:33:04.158402+00:00'
---

## Summary

Declare Atom/(.Role := Requirement)

## Claim

### Formal Claim

```python
from anechoic.formal_claims import declare_entity
from anechoic.model import Atom

class Requirement(Atom):
    pass

declare_entity(
    entity_class=Requirement,
    entity_name='Requirement',
    qualification_property_path='Atom.Header.Context.Role',
    classifications={'Role Order Number': 4},
)
```

## Semantics

A Requirement states a required outcome, behavior, property or constraint, or defines a governed model and its constraints. It applies across Aspects, including domain behavior, engineering performance, evaluation effectiveness and delivery reliability.
