---
identity:
  atom_id: AN-S-2014
context:
  container:
    component: C9
  tier: 3
  lens: DES
state:
  status: active
  version: 7
  updated_at: '2026-11-12T12:33:04.158402+00:00'
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
