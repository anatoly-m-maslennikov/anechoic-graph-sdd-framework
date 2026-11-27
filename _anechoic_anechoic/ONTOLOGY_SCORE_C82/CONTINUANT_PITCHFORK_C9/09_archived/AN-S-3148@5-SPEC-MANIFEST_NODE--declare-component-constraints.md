---
atom_family: SPEC
atom_id: AN-S-3148
container:
  component: C9
tier: 2
context:
  lens: SPEC
  template: manifest_node
state:
  status: "archived"
  version: 5
  updated_at: "2026-11-26T15:54:02.364147+00:00"
---

## Summary

Declare Component Constraints

## Claim scope

MODEL//ANECHOIC <+ Graph/Node//Artifact//SSOT//Prescribed/Structure/Component.Constraints

## Formal Manifest

```python anechoic-edsl
# Anechoic Python eDSL

from anechoic.model import Component, NodeConstraints

class Constraints(NodeConstraints):
    bearer = Component
    node.constraints.instance_relations = {'IS_CHILD_OF': {'target_entity_paths': (Component,), 'targets_per_source': 1}}
```
