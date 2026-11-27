---
atom_family: SPEC
atom_id: AN-S-2712
concern:
  subject: IS_NARROWER_THAN
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
  version: 13
  updated_at: "2026-11-26T15:52:31.205793+00:00"
---

## Summary

Define IS_NARROWER_THAN

## Claim

A narrower Model kind inherits applicable Relation and Property constraints from its broader kind. A Property does not narrow. `/` is written from broader to narrower.

## Formal Manifest

```python anechoic-edsl
# Anechoic Python eDSL

from anechoic.model import Relation

class Relation2712(Relation):
    name = 'IS_NARROWER_THAN'
    relation.source_endpoint = {'level': 'model_entities'}
    relation.target_endpoint = {'level': 'model_entities'}
    relation.acyclic = True
    relation.inverse_alias = 'HAS_NARROWER'
    relation.reverse_written_alias = '/'
```
