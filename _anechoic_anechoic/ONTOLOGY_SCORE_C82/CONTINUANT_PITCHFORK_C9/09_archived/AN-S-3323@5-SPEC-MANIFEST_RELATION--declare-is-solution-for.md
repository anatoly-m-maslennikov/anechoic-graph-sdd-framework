---
atom_family: SPEC
atom_id: AN-S-3323
container:
  component: C9
tier: 2
context:
  lens: SPEC
  template: manifest_relation
state:
  status: "archived"
  version: 5
  updated_at: "2026-11-26T15:54:02.706028+00:00"
---

## Summary

Declare IS_SOLUTION_FOR

## Claim scope

MODEL//ANECHOIC <+ Graph/Relation//IS_SOLUTION_FOR

## Semantics

The source describes how to meet a guarantee in the target Contract.

## Formal Manifest

```python anechoic-edsl
# Anechoic Python eDSL

from anechoic.model import Atom, Contract, Relation

class Relation3323(Relation):
    name = 'IS_SOLUTION_FOR'
    relation.inverse_alias = 'HAS_SOLUTION'
    relation.source_endpoint = {'level': 'instances', 'entity_paths': (Atom,)}
    relation.target_endpoint = {'level': 'instances', 'entity_paths': (Contract,)}
```
