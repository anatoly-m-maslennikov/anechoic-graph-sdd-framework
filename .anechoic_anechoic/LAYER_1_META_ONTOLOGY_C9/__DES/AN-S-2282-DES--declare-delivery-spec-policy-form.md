---
atom_family: SPEC
atom_id: AN-S-2282
structure:
  container:
    component: C9
  tier: 3
context:
  lens: DES
state:
  status: active
  version: 1
  updated_at: '2026-11-13T15:39:45.397206+00:00'
---
## Summary

Declare Delivery Spec Policy Form

## Claim

### Formal Claim

```python
from anechoic.formal_claims import declare_entity
from anechoic.model import Delivery

class DeliverySpecPolicy(Delivery):
    pass

declare_entity(
    entity_class=DeliverySpecPolicy,
    entity_name='Spec Policy',
    qualification_property_path='Atom.Header.Context.Form',
)
```

## Semantics

A Spec Policy governs how to write and review Atoms of the same Role whose main subject is its own main subject or a descendant.