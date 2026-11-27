---
atom_family: SPEC
atom_id: AN-S-4860
concern:
  subject: Constraints
  path: Model/Graph/Node//Artifact//Derived//Projection
  relation: is_property_of
container:
  component: C9
tier: 2
context:
  template: manifest_node
  lens: DOM/CONT
state:
  status: "active"
  version: 3
  updated_at: "2026-11-26T15:52:36.032166+00:00"
---

## Summary

Declare Projection Constraints

## Formal Manifest

```python anechoic-edsl
# Anechoic Python eDSL

from anechoic.model import NodeConstraints, Projection

class Constraints(NodeConstraints):
    bearer = Projection
    node.constraints.model_relations = {'IS_PROPERTY_OF': {'targets_per_source': 0}}
```
