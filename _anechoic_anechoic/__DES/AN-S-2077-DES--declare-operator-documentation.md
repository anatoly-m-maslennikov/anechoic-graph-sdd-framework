---
atom_family: SPEC
atom_id: AN-S-2077
structure:
  container:
    component: C00
  tier: 3
context:
  lens: DES
state:
  status: active
  version: 2
  updated_at: '2026-11-12T18:36:59.009278+00:00'
---
## Summary

Declare OPERATOR_DOCUMENTATION

## Claim

### Formal Claim

```python
from anechoic.formal_claims import declare_entity
from anechoic.model import ScopeUnit

declare_entity(
    entity_name='OPERATOR_DOCUMENTATION',
    instance=ScopeUnit(
        structural_level=1,
        id='CA-SU-25',
        name='OPERATOR_DOCUMENTATION',
        label='LAYER',
        ordered=True,
        order_number=3,
        container='anechoic',
    ),
)
```

