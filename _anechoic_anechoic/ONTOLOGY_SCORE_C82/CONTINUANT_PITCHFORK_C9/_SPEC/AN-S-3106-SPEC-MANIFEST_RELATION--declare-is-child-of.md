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
  status: "active"
  version: 7
  updated_at: "2026-11-25T20:23:21.941300+00:00"
---

## Summary

Declare IS_CHILD_OF

## Claim scope

MODEL//ANECHOIC <+ Graph/Relation//IS_CHILD_OF


## Claim

`IS_CHILD_OF` identifies an immediate parent. AN-S-3148 gives each Component one parent, and AN-S-3146 gives Project zero parents. `IS_PARENT_FOR` derives the immediate children from the same facts. Use the declared Project Structure for Component parentage.

## Formal Manifest

```python anechoic-edsl
# Anechoic Python eDSL

from anechoic.model import Component, Package, Relation

class Relation3106(Relation):
    name = 'IS_CHILD_OF'
    relation.acyclic = True
    relation.inverse_alias = 'IS_PARENT_FOR'
    relation.endpoint_pairs = (
        {'source_endpoint': {'level': 'instances', 'entity_paths': (Component,)}, 'target_endpoint': {'level': 'instances', 'entity_paths': (Component,)}},
        {'source_endpoint': {'level': 'instances', 'entity_paths': (Package,)}, 'target_endpoint': {'level': 'instances', 'entity_paths': (Package,)}},
    )
```
