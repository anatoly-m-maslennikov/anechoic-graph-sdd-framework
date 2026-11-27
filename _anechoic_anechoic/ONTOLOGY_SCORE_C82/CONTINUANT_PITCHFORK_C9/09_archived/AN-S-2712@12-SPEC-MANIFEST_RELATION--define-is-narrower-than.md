---
atom_family: SPEC
atom_id: AN-S-2712
container:
  component: C9
tier: 2
context:
  lens: SPEC
  template: manifest_relation
state:
  status: "archived"
  version: 12
  updated_at: "2026-11-26T15:54:01.961474+00:00"
---

## Summary

Define IS_NARROWER_THAN

## Claim scope

MODEL//ANECHOIC <+ Graph/Relation//IS_NARROWER_THAN

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
