---
atom_family: SPEC
atom_id: AN-S-2108
container:
  component: C22
tier: 3
context:
  lens: DES
state:
  status: active
  version: 1
  updated_at: '2026-11-12T19:27:00.223904+00:00'
---
## Summary

Declare PROMPTS

## Claim

### Formal Claim

```python
from anechoic.formal_claims import declare_entity
from anechoic.model import ScopeUnit

declare_entity(
    entity_name='PROMPTS',
    instance=ScopeUnit(
        id='CA-SU-24',
        name='PROMPTS',
        label='FEATURE',
        ordered=False,
        container='AGENTIC',
        structural_level=3,
    ),
)
```
