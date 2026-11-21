---
atom_family: SPEC
atom_id: AN-S-2025
container:
  component: C9
tier: 3
context:
  lens: DES
state:
  status: active
  version: 5
  updated_at: '2026-11-12T17:40:07+00:00'
---
## Summary

Declare Aspect

## Claim

### Prose Claim



- MODEL declares the generic Aspect.
- All concrete Aspects are instances in the applicable PROJECT STRUCTURE tree.

### Formal Claim

```python
from anechoic.formal_claims import declare_entity
from anechoic.model import Node

class Aspect(Node):
    pass

declare_entity(entity_class=Aspect, entity_name='Aspect')
```

## Semantics

An Aspect is a topic through which an Atom addresses its Subject.
