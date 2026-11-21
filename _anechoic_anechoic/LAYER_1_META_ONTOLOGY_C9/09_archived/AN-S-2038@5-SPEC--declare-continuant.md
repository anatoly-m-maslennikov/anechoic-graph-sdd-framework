---
atom_family: SPEC
atom_id: AN-S-2038
container:
  component: C9
tier: 2
context:
  lens: SPEC
state:
  status: archived
  version: 5
  updated_at: '2026-11-20T11:17:59+00:00'
---

## Summary

Declare Continuant

## Claim scope

MODEL//ANECHOIC <+ Continuant

## Claim

### Formal Claim

```python
from anechoic.formal_claims import declare_entity

class Continuant:
    pass

declare_entity(entity_name="Continuant", entity_class=Continuant)
```
