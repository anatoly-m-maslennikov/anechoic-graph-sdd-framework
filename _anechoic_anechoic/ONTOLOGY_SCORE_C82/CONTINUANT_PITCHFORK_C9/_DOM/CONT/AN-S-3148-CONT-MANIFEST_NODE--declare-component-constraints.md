---
atom_family: SPEC
atom_id: AN-S-3148
concern:
  subject: Constraints
  path: Model/Graph/Node//Artifact//SSOT//Prescribed/Structure/Component
  relation: is_property_of
container:
  component: C9
tier: 2
context:
  template: manifest_node
  lens: DOM/CONT
state:
  status: "active"
  version: 6
  updated_at: "2026-11-26T15:52:33.097356+00:00"
---

## Summary

Declare Component Constraints

## Formal Manifest

```python anechoic-edsl
# Anechoic Python eDSL

from anechoic.model import Component, NodeConstraints

class Constraints(NodeConstraints):
    bearer = Component
    node.constraints.instance_relations = {'IS_CHILD_OF': {'target_entity_paths': (Component,), 'targets_per_source': 1}}
```
