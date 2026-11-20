---
identity:
  atom_id: AN-S-2080
context:
  container:
    component: C00
  tier: 3
  lens: DES
state:
  status: active
  version: 2
  updated_at: '2026-11-12T18:32:26.904255+00:00'
---
## Summary

Declare FIELD

## Claim

### Formal Claim

```python
from anechoic.formal_claims import declare_entity
from anechoic.model import ScopeUnit

declare_entity(
    entity_name='FIELD',
    instance=ScopeUnit(
        structural_level=1,
        id='CA-SU-29',
        name='FIELD',
        label='FEATURE',
        ordered=False,
        container='anechoic',
    ),
)
```

