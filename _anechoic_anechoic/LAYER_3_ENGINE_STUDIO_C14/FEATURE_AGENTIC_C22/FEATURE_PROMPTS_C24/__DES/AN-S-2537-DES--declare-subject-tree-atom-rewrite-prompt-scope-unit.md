---
atom_family: SPEC
atom_id: AN-S-2537
container:
  component: C24
tier: 3
context:
  lens: DES
state:
  status: active
  version: 1
  updated_at: '2026-11-13T19:44:45.142927+00:00'
---
## Summary

Declare SUBJECT TREE ATOM REWRITE PROMPT Scope Unit

## Claim

### Formal Claim

```python
from anechoic.formal_claims import declare_entity
from anechoic.model import ScopeUnit

declare_entity(
    entity_name='SUBJECT_TREE_ATOM_REWRITE_PROMPT',
    instance=ScopeUnit(
        id='CA-SU-56',
        name='SUBJECT_TREE_ATOM_REWRITE_PROMPT',
        label='FEATURE',
        ordered=False,
        container='PROMPTS',
        structural_level=4,
    ),
)
```
