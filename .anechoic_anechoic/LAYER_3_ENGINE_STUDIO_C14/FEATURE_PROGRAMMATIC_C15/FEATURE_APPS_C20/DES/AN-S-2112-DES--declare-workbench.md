---
identity:
  atom_id: AN-S-2112
context:
  container:
    component: C20
  tier: 3
  lens: DES
state:
  status: active
  version: 1
  updated_at: '2026-11-12T19:27:09.922481+00:00'
---
## Summary

Declare WORKBENCH

## Claim

### Formal Claim

```python
from anechoic.formal_claims import declare_entity
from anechoic.model import ScopeUnit

declare_entity(
    entity_name='WORKBENCH',
    instance=ScopeUnit(
        id='CA-SU-43',
        name='WORKBENCH',
        label='APP',
        ordered=False,
        container='APPS',
        structural_level=4,
    ),
)
```
