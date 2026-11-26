---
atom_family: SPEC
atom_id: AN-S-2105
container:
  component: C9
tier: 3
context:
  lens: DES
state:
  status: "archived"
  version: 1
  updated_at: "2026-11-25T22:35:51.464090+00:00"
---
## Summary

Declare CORE_META_MODEL

## Claim

### Formal Claim

```python
from anechoic.formal_claims import declare_entity
from anechoic.model import ScopeUnit

declare_entity(
    entity_name='CORE_META_MODEL',
    instance=ScopeUnit(
        id='CA-SU-11',
        name='CORE_META_MODEL',
        label='LAYER',
        ordered=True,
        order_number=1,
        container='METHODOLOGY_SOURCES',
        structural_level=3,
    ),
)
```
