---
atom_family: SPEC
atom_id: AN-S-3106
container:
  component: C9
tier: 2
context:
  lens: SPEC
  template: manifest_relation
state:
  status: "archived"
  version: 4
  updated_at: '2026-11-24T16:58:01.361438+00:00'
---

## Summary

Declare CHILD_OF

## Claim scope

MODEL//ANECHOIC <+ Graph/Relation//CHILD_OF


## Classifications

| Relation | Transitive | Functional |
| --- | --- | --- |
| `CHILD_OF` | no | yes |
| `CHILDREN` | no | no |

`CHILD_OF` identifies an immediate parent. AN-S-3148 gives each Component one parent, and AN-S-3146 gives Project zero parents. `CHILDREN` can return multiple immediate children.

## Formal Manifest

```python anechoic-edsl
# Anechoic Python eDSL

from anechoic.model import Component, Relation

class Relation3106(Relation):
    name = 'CHILD_OF'
    acyclic = True
    inverse_alias = 'CHILDREN'
    source_endpoint = {'level': 'instances', 'entity_paths': (Component,)}
    target_endpoint = {'level': 'instances', 'entity_paths': (Component,)}
```
