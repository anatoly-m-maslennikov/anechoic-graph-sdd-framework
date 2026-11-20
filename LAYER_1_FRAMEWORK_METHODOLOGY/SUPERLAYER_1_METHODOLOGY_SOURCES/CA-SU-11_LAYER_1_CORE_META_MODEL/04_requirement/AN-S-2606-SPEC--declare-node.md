---
atom_family: SPEC
atom_id: AN-S-2606
structure:
  container:
    component: C9
context:
  lens: SPEC
state:
  status: active
  version: 11
  updated_at: '2026-11-20T14:42:07.157939+00:00'
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

declare_entity(
    entity_name='Node',
    entity_class=Node,
    entity_kind='Primary',
)
```
