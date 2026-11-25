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
  version: 3
  updated_at: '2026-11-24T16:58:01.437846+00:00'
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
    instance_relation_constraints = {'CHILD_OF': {'targets_per_source': 0}}
```
