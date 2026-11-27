---
atom_family: SPEC
atom_id: AN-S-2674
concern:
  subject: CONTAINS_RECURSIVELY
  path: Model/Graph/Relation
  relation: is_narrower_than
container:
  component: C9
tier: 2
context:
  template: manifest_relation
  lens: DOM/CONT
state:
  status: "archived"
  version: 25
  updated_at: "2026-11-26T16:34:52.349397+00:00"
---
## Summary

Derive Recursive Containment from Direct Containment

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
