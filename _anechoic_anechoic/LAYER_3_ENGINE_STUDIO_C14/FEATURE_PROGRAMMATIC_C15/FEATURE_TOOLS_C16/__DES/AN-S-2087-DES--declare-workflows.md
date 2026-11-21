---
atom_family: SPEC
atom_id: AN-S-2087
container:
  component: C16
tier: 3
context:
  lens: DES
state:
  status: active
  version: 2
  updated_at: '2026-11-12T18:32:56.578538+00:00'
---
## Summary

Declare WORKFLOWS

## Claim

### Formal Claim

```python
from anechoic.formal_claims import declare_entity
from anechoic.model import ScopeUnit

declare_entity(
    entity_name='WORKFLOWS',
    instance=ScopeUnit(
        structural_level=4,
        id='CA-SU-33',
        name='WORKFLOWS',
        label='FEATURE_GROUP',
        ordered=False,
        container='TOOLS',
    ),
)
```

