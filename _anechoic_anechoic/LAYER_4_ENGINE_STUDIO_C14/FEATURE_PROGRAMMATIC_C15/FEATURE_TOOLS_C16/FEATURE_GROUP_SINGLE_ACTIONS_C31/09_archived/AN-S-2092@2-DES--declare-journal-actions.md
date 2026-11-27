---
atom_family: SPEC
atom_id: AN-S-2092
container:
  component: C31
tier: 3
context:
  lens: DES
state:
  status: "archived"
  version: 2
  updated_at: "2026-11-27T15:07:37.342283+00:00"
---
## Summary

Declare JOURNAL_ACTIONS

## Claim

### Formal Claim

```python
from anechoic.formal_claims import declare_entity
from anechoic.model import ScopeUnit

declare_entity(
    entity_name='JOURNAL_ACTIONS',
    instance=ScopeUnit(
        structural_level=5,
        id='CA-SU-38',
        name='JOURNAL_ACTIONS',
        label='FEATURE_GROUP',
        ordered=False,
        container='SINGLE_ACTIONS',
    ),
)
```

