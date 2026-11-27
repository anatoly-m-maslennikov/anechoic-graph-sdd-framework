---
atom_family: SPEC
atom_id: AN-S-3154
container:
  component: C9
tier: 2
context:
  lens: SPEC
  template: manifest_node
state:
  status: "archived"
  version: 4
  updated_at: "2026-11-26T15:54:02.425376+00:00"
---

## Summary

Declare Contract Constraints

## Claim scope

MODEL//ANECHOIC <+ Graph/Node//Artifact//SSOT//Prescribed/Content/Atom//Specification//Contract.Constraints

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
