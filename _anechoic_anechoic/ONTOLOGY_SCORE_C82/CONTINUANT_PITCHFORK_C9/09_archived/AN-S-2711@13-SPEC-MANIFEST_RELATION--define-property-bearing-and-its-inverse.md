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
  version: 13
  updated_at: "2026-11-25T19:47:58.842977+00:00"
---

## Summary

Define Property bearing and its inverse

## Claim scope

MODEL//ANECHOIC <+ Graph/Relation//IS_PROPERTY_OF


## Classifications

| Relation | Transitive | Functional |
| --- | --- | --- |
| `IS_PROPERTY_OF` | no | yes |

The link targets the immediate bearer. AN-S-2692 requires exactly one bearer for each Property occurrence.

## Formal Manifest

```python anechoic-edsl
# Anechoic Python eDSL

from anechoic.model import Relation

class Relation2711(Relation):
    name = 'IS_PROPERTY_OF'
    relation.source_endpoint = {'level': 'model_entities'}
    relation.target_endpoint = {'level': 'model_entities'}
```
