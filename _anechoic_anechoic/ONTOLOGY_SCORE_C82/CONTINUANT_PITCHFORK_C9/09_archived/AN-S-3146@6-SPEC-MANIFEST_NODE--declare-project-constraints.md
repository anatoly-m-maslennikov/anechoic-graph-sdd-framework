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
  status: "archived"
  version: 6
  updated_at: "2026-11-26T15:54:02.347549+00:00"
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
