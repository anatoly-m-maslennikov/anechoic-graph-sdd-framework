---
identity:
  atom_id: AN-S-3152
context:
  container:
    component: C9
  lens: SPEC
state:
  status: active
  version: 1
  updated_at: '2026-11-20T14:42:07.157939+00:00'
---

## Summary

Declare Project Goal Constraints

## Claim scope

MODEL//ANECHOIC <+ Node//Artifact//Atom//Spec Atom//Purpose//Project Goal.Constraints

## Claim

### Formal Claim

```python
from anechoic.formal_claims import declare_entity
from anechoic.model import ProjectGoal

declare_entity(
    entity_name='Project Goal Constraints',
    constraints_for='Node//Artifact//Atom//Spec Atom//Purpose//Project Goal',
    instance_relation_constraints={'CONTAINED_BY': {'target_entity_paths': ('Node//Artifact//Component//Project',), 'targets_per_source': 1}},
)
```
