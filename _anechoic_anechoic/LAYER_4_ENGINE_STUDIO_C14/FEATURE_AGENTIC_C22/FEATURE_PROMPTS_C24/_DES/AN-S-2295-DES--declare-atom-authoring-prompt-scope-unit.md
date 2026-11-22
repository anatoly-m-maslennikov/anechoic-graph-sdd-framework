---
atom_family: SPEC
atom_id: AN-S-2295
container:
  component: C24
tier: 3
context:
  lens: DES
state:
  status: active
  version: 1
  updated_at: '2026-11-13T17:58:24.609338+00:00'
---
## Summary

Declare ATOM AUTHORING PROMPT Scope Unit

## Claim

### Formal Claim

```python
from anechoic.formal_claims import declare_entity
from anechoic.model import ScopeUnit

declare_entity(
    entity_name='ATOM_AUTHORING_PROMPT',
    instance=ScopeUnit(
        id='CA-SU-54',
        name='ATOM_AUTHORING_PROMPT',
        label='FEATURE',
        ordered=False,
        container='PROMPTS',
        structural_level=4,
    ),
)
```
