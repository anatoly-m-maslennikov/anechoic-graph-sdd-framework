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
  version: 4
  updated_at: '2026-11-24T23:18:33.190860+00:00'
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
    instance_relation_constraints = {'IS_CHILD_OF': {'target_entity_paths': (Component,), 'targets_per_source': 1}}
```
