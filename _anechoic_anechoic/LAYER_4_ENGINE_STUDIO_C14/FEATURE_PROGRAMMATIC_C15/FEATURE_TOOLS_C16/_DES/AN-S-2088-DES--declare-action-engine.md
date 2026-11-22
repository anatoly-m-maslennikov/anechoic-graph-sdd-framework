---
atom_family: SPEC
atom_id: AN-S-2088
container:
  component: C16
tier: 3
context:
  lens: DES
state:
  status: active
  version: 2
  updated_at: '2026-11-12T18:36:36.347383+00:00'
---
## Summary

Declare ACTION_ENGINE

## Claim

### Formal Claim

```python
from anechoic.formal_claims import declare_entity
from anechoic.model import ScopeUnit

declare_entity(
    entity_name='ACTION_ENGINE',
    instance=ScopeUnit(
        structural_level=4,
        id='CA-SU-34',
        name='ACTION_ENGINE',
        label='FEATURE_GROUP',
        ordered=False,
        container='TOOLS',
    ),
)
```

