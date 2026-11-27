---
atom_family: SPEC
atom_id: AN-S-3323
concern:
  subject: IS_SOLUTION_FOR
  path: Model/Graph/Relation
  relation: is_narrower_than
container:
  component: C9
tier: 2
context:
  template: manifest_relation
  lens: DOM/CONT
state:
  status: "active"
  version: 6
  updated_at: "2026-11-26T15:52:34.695397+00:00"
---

## Summary

Declare IS_SOLUTION_FOR

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
