---
atom_family: SPEC
atom_id: AN-S-4860
container:
  component: C9
tier: 2
context:
  lens: SPEC
  template: manifest_node
state:
  status: "archived"
  version: 1
  updated_at: '2026-11-24T22:05:05+00:00'
---

## Summary

Declare Projection Constraints

## Claim scope

MODEL//ANECHOIC <+ Graph/Node//Artifact//Derived//Projection.Constraints

## Formal Manifest

```python anechoic-edsl
# Anechoic Python eDSL

from anechoic.model import NodeConstraints, Projection

class Constraints(NodeConstraints):
    bearer = Projection
    model_relation_constraints = {'IS_PROPERTY_OF': {'targets_per_source': 0}}
```
