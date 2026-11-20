---
identity:
  atom_id: AN-S-2101
context:
  container:
    component: C14
  tier: 3
  lens: DES
state:
  status: active
  version: 1
  updated_at: '2026-11-12T19:26:52.515731+00:00'
---
## Summary

Declare PROGRAMMATIC

## Claim

### Formal Claim

```python
from anechoic.formal_claims import declare_entity
from anechoic.model import ScopeUnit

declare_entity(
    entity_name='PROGRAMMATIC',
    instance=ScopeUnit(
        id='CA-SU-15',
        name='PROGRAMMATIC',
        label='FEATURE',
        ordered=False,
        container='FRAMEWORK_ENGINE',
        structural_level=2,
    ),
)
```
