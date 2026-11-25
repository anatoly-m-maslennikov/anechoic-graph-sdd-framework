---
atom_family: SPEC
atom_id: AN-S-2014
container:
  component: C9
tier: 3
context:
  lens: DES
state:
  status: "archived"
  version: 7
  updated_at: "2026-11-25T21:25:21.477625+00:00"
---

## Summary

Declare Atom/(.Role := Delivery)

## Claim

### Formal Claim

```python
from anechoic.formal_claims import declare_entity
from anechoic.model import Atom

class Delivery(Atom):
    pass

declare_entity(
    entity_class=Delivery,
    entity_name='Delivery',
    qualification_property_path='Atom.Header.Context.Role',
    classifications={'Role Order Number': 7},
)
```

## Semantics

A Delivery specifies how results are represented, packaged, stored and made available through their Carriers at their intended destinations.
