---
identity:
  atom_id: AN-S-2024
context:
  container:
    component: C9
  tier: 3
  lens: DES
state:
  status: active
  version: 3
  updated_at: '2026-11-12T17:40:07+00:00'
---
## Summary

Declare Actor

## Claim

### Formal Claim

```python
from anechoic.formal_claims import declare_entity
from anechoic.model import Continuant

class Actor(Continuant):
    pass

declare_entity(entity_class=Actor, entity_name='Actor')
```

## Semantics

An Actor participates in Project work.
