---
identity:
  atom_id: AN-S-2190
context:
  container:
    component: C15
  tier: 1
  lens: DES
state:
  status: active
  version: 4
  updated_at: '2026-11-13T02:56:43.773790+00:00'
---

## Summary

Declare Schema Aspect

## Claim

### Prose Claim

Schema is an Engineering Aspect within Data Handling.

### Formal Claim

```python
from anechoic.formal_claims import declare_entity
from anechoic.model import Aspect
declare_entity(entity_name='Schema', instance=Aspect(address='PROJECT STRUCTURE//ANECHOIC <+ Aspects <+ Engineering <+ Operation <+ Data Handling <+ Schema'))
```

## Semantics

The structure of derived records and their declared columns, formats and generation. A schema describes data structure; it is distinct from the data values and the files carrying them.
