---
atom_family: SPEC
atom_id: AN-S-3146
concern:
  subject: Constraints
  path: Model/Graph/Node//Artifact//SSOT//Prescribed/Structure/Component//Project Spec
  relation: is_property_of
container:
  component: C9
tier: 2
context:
  template: manifest_node
  lens: DOM/CONT
state:
  status: "active"
  version: 7
  updated_at: "2026-11-26T15:52:33.033972+00:00"
---

## Summary

Declare Project Constraints

## Formal Manifest

```python anechoic-edsl
# Anechoic Python eDSL

from anechoic.model import NodeConstraints, Project

class Constraints(NodeConstraints):
    bearer = Project
    node.constraints.instance_relations = {'IS_CHILD_OF': {'targets_per_source': 0}, 'IS_CONTAINED_BY': {'targets_per_source': 0}}
```
