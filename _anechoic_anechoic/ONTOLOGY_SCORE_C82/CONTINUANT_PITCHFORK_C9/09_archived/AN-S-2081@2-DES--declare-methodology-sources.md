---
atom_family: SPEC
atom_id: AN-S-2081
container:
  component: C9
tier: 3
context:
  lens: DES
state:
  status: "archived"
  version: 2
  updated_at: "2026-11-25T23:19:26.835861+00:00"
---
## Summary

Declare METHODOLOGY_SOURCES

## Claim

### Formal Claim

```python
from anechoic.formal_claims import declare_entity
from anechoic.model import ScopeUnit

declare_entity(
    entity_name='METHODOLOGY_SOURCES',
    instance=ScopeUnit(
        structural_level=2,
        id='CA-SU-10',
        name='METHODOLOGY_SOURCES',
        label='SUPERLAYER',
        ordered=True,
        order_number=1,
        container='FRAMEWORK_METHODOLOGY',
    ),
)
```

