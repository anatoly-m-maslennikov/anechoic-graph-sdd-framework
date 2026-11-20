---
atom_family: SPEC
atom_id: AN-S-2109
structure:
  container:
    component: C22
  tier: 3
context:
  lens: DES
state:
  status: active
  version: 1
  updated_at: '2026-11-12T19:27:03.008803+00:00'
---
## Summary

Declare SKILLS

## Claim

### Formal Claim

```python
from anechoic.formal_claims import declare_entity
from anechoic.model import ScopeUnit

declare_entity(
    entity_name='SKILLS',
    instance=ScopeUnit(
        id='CA-SU-23',
        name='SKILLS',
        label='FEATURE',
        ordered=False,
        container='AGENTIC',
        structural_level=3,
    ),
)
```
