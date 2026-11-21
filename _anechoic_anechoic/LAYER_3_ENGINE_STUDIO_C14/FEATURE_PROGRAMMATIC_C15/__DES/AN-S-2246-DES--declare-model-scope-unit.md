---
atom_family: SPEC
atom_id: AN-S-2246
container:
  component: C15
tier: 3
context:
  lens: DES
state:
  status: active
  version: 1
  updated_at: '2026-11-13T15:13:40.388828+00:00'
---
## Summary

Declare MODEL Scope Unit

## Claim

### Formal Claim

```python
from anechoic.formal_claims import declare_entity
from anechoic.model import ScopeUnit

declare_entity(
    entity_name="MODEL",
    instance=ScopeUnit(
        id="CA-SU-51",
        name="MODEL",
        structural_level=3,
        label='FEATURE',
        ordered=False,
        container="PROGRAMMATIC",
    ),
)
```
