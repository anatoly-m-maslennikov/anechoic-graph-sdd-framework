---
atom_family: SPEC
atom_id: AN-S-4868
container:
  component: C9
tier: 2
context:
  lens: SPEC
  template: manifest_relation
state:
  status: "active"
  version: 2
  updated_at: "2026-11-25T16:00:38.256494+00:00"
---

## Summary

Declare CALLS_API_OF

## Claim scope

MODEL//ANECHOIC <+ Graph/Relation//CALLS_API_OF

## Semantics

Relation type: Direct. Realization Graph edge facts are derived from source evidence.

Realization Graph evidence: a resolved client in Package A calls an operation owned by Package B.
Direction: CALLS_API_OF from A to B.

Package identification follows AN-S-3159. AN-S-2611 endpoint rules apply.
Unresolved bindings emit no Package edge; retain a trace to the source.

## Formal Manifest

```python anechoic-edsl
# Anechoic Python eDSL

from anechoic.model import Package, Relation

class Relation4868(Relation):
    name = 'CALLS_API_OF'
    relation.inverse_alias = 'HAS_API_CALLER'
    relation.source_endpoint = {'level': 'instances', 'entity_paths': (Package,)}
    relation.target_endpoint = {'level': 'instances', 'entity_paths': (Package,)}
```
