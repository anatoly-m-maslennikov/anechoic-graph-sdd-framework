---
atom_family: SPEC
atom_id: AN-S-2286
structure:
  container:
    component: C51
  tier: 3
context:
  lens: DES
state:
  status: active
  version: 4
  updated_at: '2026-11-13T17:44:23.397974+00:00'
---
## Summary

Declare FORMAL MODEL ENGINE Scope Unit

## Claim

### Formal Claim

```python
from anechoic.formal_claims import declare_entity
from anechoic.model import ScopeUnit

declare_entity(
    entity_name="FORMAL_MODEL_GENERATOR",
    instance=ScopeUnit(
        id="CA-SU-50",
        name="FORMAL_MODEL_GENERATOR",
        structural_level=4,
        label="FEATURE",
        ordered=False,
        container="MODEL",
    ),
)
```
