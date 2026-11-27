---
atom_family: SPEC
atom_id: AN-S-3106
concern:
  subject: IS_CHILD_OF
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
  version: 8
  updated_at: "2026-11-26T15:52:31.765685+00:00"
---

## Summary

Declare IS_CHILD_OF

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
