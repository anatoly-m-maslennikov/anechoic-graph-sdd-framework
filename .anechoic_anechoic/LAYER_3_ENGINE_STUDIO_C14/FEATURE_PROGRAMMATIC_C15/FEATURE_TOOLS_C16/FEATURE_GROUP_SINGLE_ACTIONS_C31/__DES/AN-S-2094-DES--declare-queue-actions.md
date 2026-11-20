---
atom_family: SPEC
atom_id: AN-S-2094
structure:
  container:
    component: C31
  tier: 3
context:
  lens: DES
state:
  status: active
  version: 2
  updated_at: '2026-11-12T18:37:11.275676+00:00'
---
## Summary

Declare QUEUE_ACTIONS

## Claim

### Formal Claim

```python
from anechoic.formal_claims import declare_entity
from anechoic.model import ScopeUnit

declare_entity(
    entity_name='QUEUE_ACTIONS',
    instance=ScopeUnit(
        structural_level=5,
        id='CA-SU-40',
        name='QUEUE_ACTIONS',
        label='FEATURE_GROUP',
        ordered=False,
        container='SINGLE_ACTIONS',
    ),
)
```

