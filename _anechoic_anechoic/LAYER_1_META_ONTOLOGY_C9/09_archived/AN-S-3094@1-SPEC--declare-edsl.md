---
atom_family: SPEC
atom_id: AN-S-3094
container:
  component: C9
tier: 2
context:
  lens: SPEC
state:
  status: archived
  version: 1
  updated_at: '2026-11-20T11:17:59+00:00'
---

## Summary

Declare eDSL

## Claim scope

MODEL//ANECHOIC <+ eDSL

## Claim

### Formal Claim

```python
from anechoic.formal_claims import declare_entity

class EDSL:
    pass

declare_entity(entity_name="eDSL", entity_class=EDSL)
```
