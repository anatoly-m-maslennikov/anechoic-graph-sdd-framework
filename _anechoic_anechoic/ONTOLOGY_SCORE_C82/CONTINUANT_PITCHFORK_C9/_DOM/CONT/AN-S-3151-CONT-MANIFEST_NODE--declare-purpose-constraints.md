---
atom_family: SPEC
atom_id: AN-S-3151
concern:
  subject: Constraints
  path: Model/Graph/Node//Artifact//SSOT//Prescribed/Content/Atom//Specification//Purpose
  relation: is_property_of
container:
  component: C9
tier: 2
context:
  template: manifest_node
  lens: DOM/CONT
state:
  status: "active"
  version: 4
  updated_at: "2026-11-26T15:52:33.207813+00:00"
---

## Summary

Declare Purpose Constraints

## Formal Manifest

```python anechoic-edsl
# Anechoic Python eDSL

from anechoic.model import NodeConstraints, Purpose

def check_purpose(purpose: Purpose) -> bool:
    return bool(purpose.purpose.strip())

class Constraints(NodeConstraints):
    bearer = Purpose
    node.constraints.instance_check = check_purpose
```
