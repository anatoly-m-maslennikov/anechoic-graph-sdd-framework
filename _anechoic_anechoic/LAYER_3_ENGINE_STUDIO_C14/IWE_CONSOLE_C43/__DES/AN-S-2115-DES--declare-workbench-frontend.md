---
atom_family: SPEC
atom_id: AN-S-2115
container:
  component: C43
tier: 3
context:
  lens: DES
state:
  status: active
  version: 1
  updated_at: '2026-11-12T19:27:14.994657+00:00'
---
## Summary

Declare WORKBENCH_FRONTEND

## Claim

### Formal Claim

```python
from anechoic.formal_claims import declare_entity
from anechoic.model import ScopeUnit

declare_entity(
    entity_name='WORKBENCH_FRONTEND',
    instance=ScopeUnit(
        id='CA-SU-46',
        name='WORKBENCH_FRONTEND',
        label='FEATURE',
        ordered=False,
        container='WORKBENCH',
        structural_level=5,
    ),
)
```
