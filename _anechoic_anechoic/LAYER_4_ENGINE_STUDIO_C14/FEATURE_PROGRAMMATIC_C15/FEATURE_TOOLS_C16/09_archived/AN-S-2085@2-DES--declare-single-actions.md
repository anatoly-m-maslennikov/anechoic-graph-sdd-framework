---
atom_family: SPEC
atom_id: AN-S-2085
container:
  component: C16
tier: 3
context:
  lens: DES
state:
  status: "archived"
  version: 2
  updated_at: "2026-11-27T15:07:37.342283+00:00"
---
## Summary

Declare SINGLE_ACTIONS

## Claim

### Formal Claim

```python
from anechoic.formal_claims import declare_entity
from anechoic.model import ScopeUnit

declare_entity(
    entity_name='SINGLE_ACTIONS',
    instance=ScopeUnit(
        structural_level=4,
        id='CA-SU-31',
        name='SINGLE_ACTIONS',
        label='FEATURE_GROUP',
        ordered=False,
        container='TOOLS',
    ),
)
```

