---
atom_family: SPEC
atom_id: AN-S-4338
container:
  component: C9
tier: 3
context:
  lens: DES
state:
  status: archived
  version: 1
  updated_at: '2026-11-12T20:08:11.332062+00:00'
---

## Summary

Declare Delivery Approach Policy Form

## Claim

### Formal Claim

```python
from anechoic.formal_claims import declare_entity
from anechoic.model import Delivery

class ApproachPolicy(Delivery):
    pass

declare_entity(
    entity_class=ApproachPolicy,
    entity_name='Approach Policy',
    qualification_property_path='Atom.Header.Context.Form',
)
```

## Semantics

An Approach Policy is conditional on its stated case. At every descendant where that case applies, a local Atom must bind the Policy to the actual case through SPECIALIZES. A reference alone is insufficient; the binding preserves parent constraints.
