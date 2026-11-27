---
atom_family: SPEC
atom_id: AN-S-2100
container:
  component: C14
tier: 3
context:
  lens: DES
state:
  status: "archived"
  version: 1
  updated_at: "2026-11-27T15:07:37.342283+00:00"
---
## Summary

Declare AGENTIC

## Claim

### Formal Claim

```python
from anechoic.formal_claims import declare_entity
from anechoic.model import ScopeUnit

declare_entity(
    entity_name='AGENTIC',
    instance=ScopeUnit(
        id='CA-SU-22',
        name='AGENTIC',
        label='FEATURE',
        ordered=False,
        container='FRAMEWORK_ENGINE',
        structural_level=2,
    ),
)
```
