---
atom_family: SPEC
atom_id: AN-S-2086
container:
  component: C16
tier: 3
context:
  lens: DES
state:
  status: active
  version: 2
  updated_at: '2026-11-12T18:29:59.066685+00:00'
---
## Summary

Declare SCHEDULERS

## Claim

### Formal Claim

```python
from anechoic.formal_claims import declare_entity
from anechoic.model import ScopeUnit

declare_entity(
    entity_name='SCHEDULERS',
    instance=ScopeUnit(
        structural_level=4,
        id='CA-SU-32',
        name='SCHEDULERS',
        label='FEATURE_GROUP',
        ordered=False,
        container='TOOLS',
    ),
)
```

