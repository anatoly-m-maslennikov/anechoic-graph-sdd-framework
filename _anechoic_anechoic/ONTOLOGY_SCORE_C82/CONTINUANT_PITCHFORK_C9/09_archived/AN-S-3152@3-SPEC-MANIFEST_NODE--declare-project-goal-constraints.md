---
atom_family: SPEC
atom_id: AN-S-3152
container:
  component: C9
tier: 2
context:
  lens: SPEC
  template: manifest_node
state:
  status: "archived"
  version: 3
  updated_at: '2026-11-24T23:18:33.190860+00:00'
---

## Summary

Declare Project Goal Constraints

## Claim scope

MODEL//ANECHOIC <+ Graph/Node//Artifact//SSOT//Prescribed/Content/Atom//Specification//Purpose//Project Goal.Constraints

## Formal Manifest

```python anechoic-edsl
# Anechoic Python eDSL

from anechoic.model import NodeConstraints, Project, ProjectGoal

class Constraints(NodeConstraints):
    bearer = ProjectGoal
    instance_relation_constraints = {'IS_CONTAINED_BY': {'target_entity_paths': (Project,), 'targets_per_source': 1}}
```
