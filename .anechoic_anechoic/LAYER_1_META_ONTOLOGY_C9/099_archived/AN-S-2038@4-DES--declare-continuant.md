---
identity:
  atom_id: AN-S-2038
context:
  container:
    component: C9
  tier: 3
  lens: DES
state:
  status: archived
  version: 4
  updated_at: '2026-11-12T17:40:07+00:00'
---

## Summary

Declare Continuant

## Claim

### Formal Claim

```python
from anechoic.formal_claims import declare_entity
from anechoic.model import Node

class Continuant(Node):
    pass

declare_entity(entity_class=Continuant, entity_name='Continuant')
```

## Semantics

A Continuant persists as an identifiable thing.
