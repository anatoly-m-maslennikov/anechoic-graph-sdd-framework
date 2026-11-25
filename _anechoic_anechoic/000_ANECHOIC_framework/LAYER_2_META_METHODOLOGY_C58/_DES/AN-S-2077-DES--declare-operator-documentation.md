---
atom_family: SPEC
atom_id: AN-S-2077
container:
  component: C00
tier: 3
context:
  lens: DES
state:
  status: active
  version: 3
  updated_at: '2026-11-24T14:38:16.546723+00:00'
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
        order_number=6,
        container='anechoic',
    ),
)
```

