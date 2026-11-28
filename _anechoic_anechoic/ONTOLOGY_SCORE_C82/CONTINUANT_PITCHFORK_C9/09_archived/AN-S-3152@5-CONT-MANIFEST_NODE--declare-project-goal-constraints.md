---
atom_family: SPEC
atom_id: AN-S-3152
concern:
  subject: Constraints
  path: Model/Graph/Node//Artifact//SSOT//Prescribed/Content/Atom//Specification//Purpose//Project Goal
  relation: is_property_of
container:
  component: C9
tier: 2
context:
  template: manifest_node
  lens: DOM/CONT
state:
  status: archived
  version: 5
  updated_at: "2026-11-26T15:52:33.265986+00:00"
---

## Summary

Declare Project Goal Constraints

## Formal Manifest

```python anechoic-edsl
# Anechoic Python eDSL

from anechoic.model import NodeConstraints, Project, ProjectGoal

class Constraints(NodeConstraints):
    bearer = ProjectGoal
    node.constraints.instance_relations = {'IS_CONTAINED_BY': {'target_entity_paths': (Project,), 'targets_per_source': 1}}
```
