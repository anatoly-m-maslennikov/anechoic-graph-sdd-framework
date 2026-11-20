---
identity:
  atom_id: AN-S-3096
context:
  container:
    component: C9
  lens: SPEC
state:
  status: active
  version: 1
  updated_at: '2026-11-20T11:17:59+00:00'
---

## Summary

Declare Ephemeral

## Claim scope

MODEL//ANECHOIC <+ Node//Ephemeral

## Claim

### Formal Claim

```python
from anechoic.formal_claims import declare_entity
from anechoic.model import Node

class Ephemeral(Node):
    pass

declare_entity(entity_name="Ephemeral", entity_class=Ephemeral)
```
