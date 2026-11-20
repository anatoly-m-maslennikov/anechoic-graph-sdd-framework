---
atom_family: SPEC
atom_id: AN-S-2200
structure:
  container:
    component: C9
context:
  lens: SPEC
state:
  status: archived
  version: 6
  updated_at: '2026-11-20T11:17:59+00:00'
---

## Summary

Define View

## Claim scope

MODEL//ANECHOIC <+ View

## Claim

### Formal Claim

```python
from anechoic.formal_claims import declare_entity

class View:
    pass

declare_entity(entity_name="View", entity_class=View)
```
