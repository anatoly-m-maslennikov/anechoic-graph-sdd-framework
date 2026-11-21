---
atom_family: SPEC
atom_id: AN-S-2106
structure:
  container:
    component: C15
  tier: 3
context:
  lens: DES
state:
  status: active
  version: 1
  updated_at: '2026-11-12T19:26:47.801516+00:00'
---
## Summary

Declare MCP

## Claim

### Formal Claim

```python
from anechoic.formal_claims import declare_entity
from anechoic.model import ScopeUnit

declare_entity(
    entity_name='MCP',
    instance=ScopeUnit(
        id='CA-SU-21',
        name='MCP',
        label='FEATURE',
        ordered=False,
        container='PROGRAMMATIC',
        structural_level=3,
    ),
)
```
