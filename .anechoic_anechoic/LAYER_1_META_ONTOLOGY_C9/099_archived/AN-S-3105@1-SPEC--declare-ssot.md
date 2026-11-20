---
atom_family: SPEC
atom_id: AN-S-3105
structure:
  container:
    component: C9
context:
  lens: SPEC
state:
  status: archived
  version: 1
  updated_at: '2026-11-20T11:17:59+00:00'
---

## Summary

Declare SSOT

## Claim scope

MODEL//ANECHOIC <+ SSOT

## Claim

### Formal Claim

```python
from anechoic.formal_claims import declare_entity

class SSOT:
    pass

declare_entity(entity_name="SSOT", entity_class=SSOT)
```
