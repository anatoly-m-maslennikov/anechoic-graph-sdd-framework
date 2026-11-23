---
atom_family: SPEC
atom_id: AN-S-2286
container:
  component: C15
tier: 3
context:
  lens: DES
state:
  status: archived
  version: 2
  updated_at: '2026-11-12T18:25:04.925507+00:00'
---
## Summary

Declare FORMAL MODEL ENGINE Scope Unit

## Claim

### Formal Claim

```python
from anechoic.formal_claims import declare_entity
from anechoic.model import ScopeUnit

declare_entity(
    entity_name='FORMAL_MODEL_ENGINE',
    instance=ScopeUnit(
        id='CA-SU-50',
        name='FORMAL_MODEL_ENGINE',
        structural_level=3,
        label='FEATURE',
        ordered=False,
        container='PROGRAMMATIC',
    ),
)
```
