---
atom_family: SPEC
atom_id: AN-S-2540
container:
  component: C24
tier: 3
context:
  lens: DES
state:
  status: active
  version: 1
  updated_at: '2026-11-13T19:52:51.241737+00:00'
---
## Summary

Declare SUBJECT ATOM GATHERER PROMPT Scope Unit

## Claim

### Formal Claim

```python
from anechoic.formal_claims import declare_entity
from anechoic.model import ScopeUnit

declare_entity(
    entity_name='SUBJECT_ATOM_GATHERER_PROMPT',
    instance=ScopeUnit(
        id='CA-SU-57',
        name='SUBJECT_ATOM_GATHERER_PROMPT',
        label='FEATURE',
        ordered=False,
        container='PROMPTS',
        structural_level=4,
    ),
)
```
