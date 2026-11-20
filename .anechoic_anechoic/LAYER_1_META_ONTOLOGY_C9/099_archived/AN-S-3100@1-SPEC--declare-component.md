---
identity:
  atom_id: AN-S-3100
context:
  container:
    component: C9
  lens: SPEC
state:
  status: archived
  version: 1
  updated_at: '2026-11-20T11:17:59+00:00'
---

## Summary

Declare Component

## Claim scope

MODEL//ANECHOIC <+ Node//Artifact//Component

## Claim

### Formal Claim

```python
from anechoic.formal_claims import declare_entity
from anechoic.model import Artifact

class Component(Artifact):
    pass

declare_entity(entity_name="Component", entity_class=Component,
    instance_relation_constraints={
        "CHILD_OF": {"target_entity_paths": ("Node//Artifact//Component",), "targets_per_source": 1},
    },
)
```
