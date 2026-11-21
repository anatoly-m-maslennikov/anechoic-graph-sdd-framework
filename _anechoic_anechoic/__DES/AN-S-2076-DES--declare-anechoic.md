---
atom_family: SPEC
atom_id: AN-S-2076
structure:
  container:
    component: C00
  tier: 3
context:
  lens: DES
state:
  status: active
  version: 2
  updated_at: 2026-11-05 12:58:42 +0400
---
## Summary

Declare anechoic

## Claim

### Formal Claim

```python
from anechoic.formal_claims import declare_entity
from anechoic.model import Project

declare_entity(
    entity_name='anechoic',
    instance=Project(
        id='CA-SU-00',
        name='anechoic',
        structural_level=0,
    ),
)
```
