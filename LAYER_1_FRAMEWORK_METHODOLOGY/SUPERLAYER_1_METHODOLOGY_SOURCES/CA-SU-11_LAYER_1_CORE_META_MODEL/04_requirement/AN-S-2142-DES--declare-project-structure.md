---
atom_family: SPEC
atom_id: AN-S-2142
structure:
  container:
    component: C9
  tier: 3
context:
  lens: DES
state:
  status: active
  version: 3
  updated_at: '2026-11-12T20:21:37.628721+00:00'
---
## Summary

Declare PROJECT STRUCTURE

## Claim

### Formal Claim

```python
from anechoic.formal_claims import declare_entity
from anechoic.model import Node

class ProjectStructure(Node):
    pass

declare_entity(
    entity_class=ProjectStructure,
    entity_name='PROJECT STRUCTURE',
    model_relation_constraints={"IS_PROPERTY_OF": {"targets_per_source": 0}},
    classifications={"Container": "yes"},
)
```

## Semantics

PROJECT STRUCTURE describes the actual structure of a Project, including its Scope Units, Aspects, and other declared components.
