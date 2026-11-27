---
atom_family: SPEC
atom_id: AN-S-2674
container:
  component: C9
tier: 2
context:
  lens: SPEC
  template: manifest_relation
state:
  status: "archived"
  version: 24
  updated_at: "2026-11-26T15:54:01.908626+00:00"
---
## Summary

Derive Recursive Containment from Direct Containment

## Claim scope

MODEL//ANECHOIC <+ Graph/Relation//CONTAINS_RECURSIVELY

## Semantics

The source recursively contains the target when one or more successive `CONTAINS` links lead from source to target.

## Classifications

| Relation | Transitive | Functional |
| --- | --- | --- |
| `CONTAINS_RECURSIVELY` | yes | no |

## Formal Manifest

```python anechoic-edsl
# Anechoic Python eDSL

from anechoic.model import Relation

class ContainsRecursively(Relation):
    name = 'CONTAINS_RECURSIVELY'
    relation.derived_from = 'CONTAINS'
    relation.source_endpoint = {'level': 'model_entities_or_instances'}
    relation.target_endpoint = {'level': 'model_entities_or_instances'}
```
