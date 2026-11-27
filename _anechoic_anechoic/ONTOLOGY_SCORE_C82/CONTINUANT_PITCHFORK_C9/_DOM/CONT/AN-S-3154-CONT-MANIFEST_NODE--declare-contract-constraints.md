---
atom_family: SPEC
atom_id: AN-S-3154
concern:
  subject: Constraints
  path: Model/Graph/Node//Artifact//SSOT//Prescribed/Content/Atom//Specification//Contract
  relation: is_property_of
container:
  component: C9
tier: 2
context:
  template: manifest_node
  lens: DOM/CONT
state:
  status: "active"
  version: 5
  updated_at: "2026-11-26T15:52:33.306949+00:00"
---

## Summary

Declare Contract Constraints

## Formal Manifest

```python anechoic-edsl
# Anechoic Python eDSL

from anechoic.model import Component, Contract, NodeConstraints

def check_contract(contract: Contract) -> bool:
    return bool(contract.guarantee.strip())

class Constraints(NodeConstraints):
    bearer = Contract
    node.constraints.instance_check = check_contract
    node.constraints.instance_relations = {'IS_CONTAINED_BY': {'target_entity_paths': (Component,), 'targets_per_source': 1}}
```
