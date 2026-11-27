---
atom_family: SPEC
atom_id: AN-S-2190
container:
  component: C15
tier: 1
context:
  lens: DES
state:
  status: active
  version: 5
  updated_at: "2026-11-27T16:29:34.309627+00:00"
---

## Summary

Declare Schema Aspect

## Claim

### Formal Claim

```python
from anechoic.formal_claims import declare_entity
from anechoic.model import Aspect
declare_entity(entity_name='Schema', instance=Aspect(address='PROJECT STRUCTURE//ANECHOIC <+ Aspects <+ Engineering <+ Operation <+ Data Handling <+ Schema'))
```

## Semantics

The structure of derived records and their declared columns, formats and generation. A schema describes data structure; it is distinct from the data values and the files carrying them.
