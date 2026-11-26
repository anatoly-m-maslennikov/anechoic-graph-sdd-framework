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
  version: 3
  updated_at: '2026-11-24T23:18:33.190860+00:00'
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
    instance_check = check_contract
    instance_relation_constraints = {'IS_CONTAINED_BY': {'target_entity_paths': (Component,), 'targets_per_source': 1}}
```
