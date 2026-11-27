---
atom_family: SPEC
atom_id: AN-S-2711
container:
  component: C9
tier: 2
context:
  lens: SPEC
  template: manifest_relation
state:
  status: "archived"
  version: 15
  updated_at: "2026-11-26T15:54:01.948347+00:00"
---

## Summary

Define Property bearing and its inverse

## Claim scope

MODEL//ANECHOIC <+ Graph/Relation//IS_PROPERTY_OF


## Classifications

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
    relation.acyclic = True
    relation.source_endpoint = {'level': 'model_entities'}
    relation.target_endpoint = {'level': 'model_entities'}
```
