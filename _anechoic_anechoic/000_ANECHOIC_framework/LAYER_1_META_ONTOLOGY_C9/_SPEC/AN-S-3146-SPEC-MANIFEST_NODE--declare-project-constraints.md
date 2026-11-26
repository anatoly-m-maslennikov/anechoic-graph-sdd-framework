---
atom_family: SPEC
atom_id: AN-S-3146
container:
  component: C9
tier: 2
context:
  lens: SPEC
  template: manifest_node
state:
  status: "active"
  version: 6
  updated_at: "2026-11-25T16:00:37.951902+00:00"
---

## Summary

Declare Project Constraints

## Claim scope

MODEL//ANECHOIC <+ Graph/Node//Artifact//SSOT//Prescribed/Structure/Component//Project Spec.Constraints

## Formal Manifest

```python anechoic-edsl
# Anechoic Python eDSL

from anechoic.model import NodeConstraints, Project

class Constraints(NodeConstraints):
    bearer = Project
    node.constraints.instance_relations = {'IS_CHILD_OF': {'targets_per_source': 0}, 'IS_CONTAINED_BY': {'targets_per_source': 0}}
```
