---
atom_family: SPEC
atom_id: AN-S-2008
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

Declare Operations

## Claim

### Formal Claim

```python
from anechoic.formal_claims import declare_entity
from anechoic.model import Atom

class Operations(Atom):
    pass

declare_entity(
    entity_class=Operations,
    entity_name='Operations',
    qualification_property_path='Atom.Header.Context.Role',
    classifications={'Role Order Number': 9},
)
```

## Semantics

An Operations Atom specifies work to perform and how it is coordinated, including its sequence, inputs and outputs.
