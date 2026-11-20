---
atom_family: SPEC
atom_id: AN-S-2697
structure:
  container:
    component: C9
context:
  lens: SPEC
state:
  status: archived
  version: 17
  updated_at: '2026-11-20T11:17:59+00:00'
---

## Summary

Define Relation

## Claim scope

MODEL//ANECHOIC <+ Graph/Relation

## Claim

### Formal Claim

```python
from anechoic.formal_claims import declare_entity

class Relation:
    pass

declare_entity(entity_name="Relation", entity_class=Relation)
```
