---
atom_family: SPEC
atom_id: AN-S-2079
structure:
  container:
    component: C00
  tier: 3
context:
  lens: DES
state:
  status: active
  version: 2
  updated_at: '2026-11-12T18:36:44.625027+00:00'
---
## Summary

Declare COMMUNITY_EXTENSIONS

## Claim

### Formal Claim

```python
from anechoic.formal_claims import declare_entity
from anechoic.model import ScopeUnit

declare_entity(
    entity_name='COMMUNITY_EXTENSIONS',
    instance=ScopeUnit(
        structural_level=1,
        id='CA-SU-28',
        name='COMMUNITY_EXTENSIONS',
        label='FEATURE',
        ordered=False,
        container='anechoic',
    ),
)
```

