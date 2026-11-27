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
  version: 2
  updated_at: "2026-11-26T15:54:03.086753+00:00"
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
    node.constraints.model_relations = {'IS_PROPERTY_OF': {'targets_per_source': 0}}
```
