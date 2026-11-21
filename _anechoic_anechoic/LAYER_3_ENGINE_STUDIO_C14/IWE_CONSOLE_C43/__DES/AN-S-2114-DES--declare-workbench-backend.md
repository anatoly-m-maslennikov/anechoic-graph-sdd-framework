---
atom_family: SPEC
atom_id: AN-S-2114
structure:
  container:
    component: C43
  tier: 3
context:
  lens: DES
state:
  status: active
  version: 1
  updated_at: '2026-11-12T19:27:12.060587+00:00'
---
## Summary

Declare WORKBENCH_BACKEND

## Claim

### Formal Claim

```python
from anechoic.formal_claims import declare_entity
from anechoic.model import ScopeUnit

declare_entity(
    entity_name='WORKBENCH_BACKEND',
    instance=ScopeUnit(
        id='CA-SU-45',
        name='WORKBENCH_BACKEND',
        label='FEATURE',
        ordered=False,
        container='WORKBENCH',
        structural_level=5,
    ),
)
```
