---
atom_family: SPEC
atom_id: AN-S-3151
container:
  component: C9
tier: 2
context:
  lens: SPEC
  template: manifest_node
state:
  status: "active"
  version: 3
  updated_at: "2026-11-25T16:00:37.977023+00:00"
---

## Summary

Declare Purpose Constraints

## Claim scope

MODEL//ANECHOIC <+ Graph/Node//Artifact//SSOT//Prescribed/Content/Atom//Specification//Purpose.Constraints

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
