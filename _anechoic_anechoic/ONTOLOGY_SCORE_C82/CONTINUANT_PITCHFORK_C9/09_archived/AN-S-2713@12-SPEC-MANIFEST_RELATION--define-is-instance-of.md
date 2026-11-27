---
atom_family: SPEC
atom_id: AN-S-2713
container:
  component: C9
tier: 2
context:
  lens: SPEC
  template: manifest_relation
state:
  status: "archived"
  version: 12
  updated_at: "2026-11-26T15:54:01.968802+00:00"
---

## Summary

Define IS_INSTANCE_OF

## Claim scope

MODEL//ANECHOIC <+ Graph/Relation//IS_INSTANCE_OF

## Claim

An instance relates to its declared Model entity. A Property instance is borne by its data bearer, has no independent Carrier, and is an instance of its corresponding model Property. The inverse alias reverses the same fact.

## Formal Manifest

```python anechoic-edsl
# Anechoic Python eDSL

from anechoic.model import Relation

class Relation2713(Relation):
    name = 'IS_INSTANCE_OF'
    relation.source_endpoint = {'level': 'instances'}
    relation.target_endpoint = {'level': 'model_entities'}
    relation.inverse_alias = 'HAS_INSTANCE'
    relation.written_alias = '//'
```
