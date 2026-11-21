---
atom_family: SPEC
atom_id: AN-S-2097
structure:
  container:
    component: C00
  tier: 3
context:
  lens: DES
state:
  status: active
  version: 1
  updated_at: '2026-11-12T19:26:37.054388+00:00'
---
## Summary

Declare FRAMEWORK_DELIVERY

## Claim

### Formal Claim

```python
from anechoic.formal_claims import declare_entity
from anechoic.model import ScopeUnit

declare_entity(
    entity_name='FRAMEWORK_DELIVERY',
    instance=ScopeUnit(
        id='CA-SU-27',
        name='FRAMEWORK_DELIVERY',
        label='LAYER',
        ordered=True,
        order_number=5,
        container='anechoic',
        structural_level=1,
    ),
)
```
