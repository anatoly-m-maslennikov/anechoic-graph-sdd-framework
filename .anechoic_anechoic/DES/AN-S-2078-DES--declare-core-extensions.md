---
identity:
  atom_id: AN-S-2078
context:
  container:
    component: C00
  tier: 3
  lens: DES
state:
  status: active
  version: 2
  updated_at: '2026-11-12T18:36:47.434948+00:00'
---
## Summary

Declare CORE_EXTENSIONS

## Claim

### Formal Claim

```python
from anechoic.formal_claims import declare_entity
from anechoic.model import ScopeUnit

declare_entity(
    entity_name='CORE_EXTENSIONS',
    instance=ScopeUnit(
        structural_level=1,
        id='CA-SU-26',
        name='CORE_EXTENSIONS',
        label='LAYER',
        ordered=True,
        order_number=4,
        container='anechoic',
    ),
)
```

