---
atom_family: SPEC
atom_id: AN-S-2039
structure:
  container:
    component: C9
  tier: 3
context:
  lens: DES
state:
  status: archived
  version: 4
  updated_at: '2026-11-12T17:40:07+00:00'
---

## Summary

Declare Occurrent

## Claim

### Formal Claim

```python
from anechoic.formal_claims import declare_entity
from anechoic.model import Node

class Occurrent(Node):
    pass

declare_entity(entity_class=Occurrent, entity_name='Occurrent')
```

## Semantics

An Occurrent is an actual occurrence unfolding in time. A record describes an occurrence; it is distinct from the occurrence itself.
