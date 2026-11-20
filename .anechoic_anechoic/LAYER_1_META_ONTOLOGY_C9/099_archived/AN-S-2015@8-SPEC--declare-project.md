---
identity:
  atom_id: AN-S-2015
context:
  container:
    component: C9
  lens: SPEC
state:
  status: archived
  version: 8
  updated_at: '2026-11-20T11:17:59+00:00'
---

## Summary

Declare Project

## Claim scope

MODEL//ANECHOIC <+ Node//Artifact//Component//Project

## Claim

### Formal Claim

```python
from anechoic.formal_claims import declare_entity
from anechoic.model import Component

class Project(Component):
    pass

declare_entity(entity_name="Project", entity_class=Project,
    instance_relation_constraints={"CHILD_OF": {"targets_per_source": 0}},
)
```
