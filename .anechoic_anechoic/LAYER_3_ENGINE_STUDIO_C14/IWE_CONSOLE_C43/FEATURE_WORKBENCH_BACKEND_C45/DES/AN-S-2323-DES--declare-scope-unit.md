---
identity:
  atom_id: AN-S-2323
context:
  container:
    component: C45
  lens: DES
state:
  status: active
  version: 1
  updated_at: 2026-11-12 20:26:29 +0000
---
## Summary

Declare Scope Unit

## Claim

### Formal Claim

```python
from anechoic.formal_claims import declare_entity
from anechoic.model import ScopeUnit

declare_entity(
    entity_name='WORKBENCH_BURST_500_RENAMED',
    instance=ScopeUnit(
        id='CA-SU-910647071',
        name='WORKBENCH_BURST_500_RENAMED',
        structural_level=6,
        label='FEATURE',
        ordered=False,
        container='WORKBENCH_BACKEND',
    ),
)
```
