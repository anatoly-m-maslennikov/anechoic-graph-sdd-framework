---
identity:
  atom_id: AN-S-1999
context:
  container:
    component: C9
  tier: 1
  lens: DES
state:
  status: active
  version: 17
  updated_at: '2026-11-12T17:40:07+00:00'
---
## Summary

Define Entity/Carrier

## Claim

### Prose Claim

A Carrier is a storage representation distinct from the Object it represents. An Object is an instance of any model Entity.

### Formal Claim

```python
from anechoic.formal_claims import declare_entity

class Carrier:
    pass

declare_entity(entity_class=Carrier, entity_name='Carrier')
```

