---
atom_family: SPEC
atom_id: AN-S-2600
container:
  component: C9
tier: 3
context:
  lens: DES
state:
  status: "archived"
  version: 5
  updated_at: "2026-11-25T23:01:34.403999+00:00"
---

## Summary

Declare Action

## Claim

### Formal Claim

```python
from anechoic.formal_claims import Cardinality, declare_entity
from anechoic.model import Operations

class Action(Operations):
    pass

declare_entity(
    entity_name='Action', entity_class=Action,
    instance_relation_constraints={
        'IS_RUN_BY': {'target_entity_paths': ('Atom/(.Header.Context.Role:=Operations)/Step',), 'targets_per_source': Cardinality(minimum=0, maximum=None)},
    },
)
```

## Semantics

An Action is a reusable operational building block. Its boundary reflects one modeled responsibility.
