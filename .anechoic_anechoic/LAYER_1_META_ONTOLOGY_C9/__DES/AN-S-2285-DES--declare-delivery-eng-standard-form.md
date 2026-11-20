---
atom_family: SPEC
atom_id: AN-S-2285
structure:
  container:
    component: C9
  tier: 3
context:
  lens: DES
state:
  status: active
  version: 1
  updated_at: '2026-11-13T15:40:01.174594+00:00'
---
## Summary

Declare Delivery Eng Standard Form

## Claim

### Formal Claim

```python
from anechoic.formal_claims import declare_entity
from anechoic.model import Delivery

class DeliveryEngStandard(Delivery):
    pass

declare_entity(
    entity_class=DeliveryEngStandard,
    entity_name='Eng Standard',
    qualification_property_path='Atom.Header.Context.Form',
)
```

## Semantics

An Eng Standard applies directly to implementation within its owning Scope Unit and descendant Scope Units where its Claim applies.