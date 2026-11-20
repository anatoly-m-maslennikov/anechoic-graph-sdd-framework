---
identity:
  atom_id: AN-S-2606
context:
  container:
    component: C9
  lens: SPEC
state:
  status: active
  version: 10
  updated_at: '2026-11-20T11:17:59+00:00'
---

## Summary

Declare Node

## Claim scope

MODEL//ANECHOIC <+ Node

## Claim

### Formal Claim

```python
from anechoic.formal_claims import declare_entity

class Node:
    pass

declare_entity(entity_name="Node", entity_class=Node)
```
