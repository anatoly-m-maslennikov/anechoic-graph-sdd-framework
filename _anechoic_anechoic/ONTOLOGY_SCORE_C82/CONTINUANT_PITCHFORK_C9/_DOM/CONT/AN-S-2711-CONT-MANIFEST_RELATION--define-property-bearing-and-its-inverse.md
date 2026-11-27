---
atom_family: SPEC
atom_id: AN-S-2711
concern:
  subject: IS_PROPERTY_OF
  path: Model/Graph/Relation
  relation: is_narrower_than
container:
  component: C9
tier: 2
context:
  template: manifest_relation
  lens: DOM/CONT
state:
  status: active
  version: 18
  updated_at: '2026-11-26T18:34:31.644797+00:00'
---

## Summary

Define Property bearing and its inverse

## Axes

| Relation | Transitive | Functional |
| --- | --- | --- |
| `IS_PROPERTY_OF` | no | yes |

Each declared Property occurrence has exactly one immediate bearer. Its bearer qualifies its identity. A missing bearer invalidates the occurrence.

## Formal Manifest

```python anechoic-edsl
# Anechoic Python eDSL

from anechoic.model import Relation

class Relation2711(Relation):
    name = 'IS_PROPERTY_OF'
    relation.inverse_alias = 'HAS_PROPERTY'
    relation.acyclic = True
    relation.source_endpoint = {'level': 'model_entities'}
    relation.target_endpoint = {'level': 'model_entities'}
```
