---
atom_family: SPEC
atom_id: AN-S-3146
container:
  component: C9
tier: 2
context:
  lens: SPEC
state:
  status: draft
  version: 2
  updated_at: '2026-11-21T13:03:17+00:00'
---

## Summary

Declare Project Constraints

## Claim scope

MODEL//ANECHOIC <+ Node//Artifact//Component//Project.Constraints

## Claim

### Formal Claim

```python
from anechoic.formal_claims import declare_entity
from anechoic.model import Project

declare_entity(
    entity_name='Project Constraints',
    constraints_for='Node//Artifact//Component//Project',
    instance_relation_constraints={'IS_CHILD_OF': {'targets_per_source': 0}},
)
```
