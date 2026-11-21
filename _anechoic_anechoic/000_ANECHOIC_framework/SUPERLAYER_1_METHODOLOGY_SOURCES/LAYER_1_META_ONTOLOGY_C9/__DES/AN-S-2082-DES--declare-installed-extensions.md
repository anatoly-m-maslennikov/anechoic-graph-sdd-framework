---
atom_family: SPEC
atom_id: AN-S-2082
container:
  component: C9
tier: 3
context:
  lens: DES
state:
  status: active
  version: 2
  updated_at: '2026-11-12T18:36:50.530980+00:00'
---
## Summary

Declare INSTALLED_EXTENSIONS

## Claim

### Formal Claim

```python
from anechoic.formal_claims import declare_entity
from anechoic.model import ScopeUnit

declare_entity(
    entity_name='INSTALLED_EXTENSIONS',
    instance=ScopeUnit(
        structural_level=3,
        id='CA-SU-12',
        name='INSTALLED_EXTENSIONS',
        label='LAYER',
        ordered=True,
        order_number=2,
        container='METHODOLOGY_SOURCES',
    ),
)
```

