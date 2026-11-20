---
identity:
  atom_id: AN-S-2789
context:
  container:
    component: C9
  lens: SPEC
state:
  status: archived
  version: 9
  updated_at: '2026-11-20T11:17:59+00:00'
---

## Summary

Define Cardinality

## Claim scope

MODEL//ANECHOIC <+ eDSL/Cardinality

## Claim

### Formal Claim

```python
from anechoic.formal_claims import declare_entity

class Cardinality:
    pass

declare_entity(entity_name="Cardinality", entity_class=Cardinality)
```
