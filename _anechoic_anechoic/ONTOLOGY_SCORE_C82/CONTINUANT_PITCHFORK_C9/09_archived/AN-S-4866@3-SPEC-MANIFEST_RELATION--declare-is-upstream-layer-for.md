---
atom_family: SPEC
atom_id: AN-S-4866
container:
  component: C9
tier: 2
context:
  lens: SPEC
  template: manifest_relation
state:
  status: "archived"
  version: 3
  updated_at: "2026-11-26T15:54:03.122959+00:00"
---

## Summary

Declare IS_UPSTREAM_LAYER_FOR

## Claim scope

MODEL//ANECHOIC <+ Graph/Relation//IS_UPSTREAM_LAYER_FOR

## Semantics

Relation type: Direct. Realization Graph edge facts are derived from source evidence.

Realization Graph evidence: Package A and Package B are in the same ordered sibling group, and A has the lower layer number.
Direction: IS_UPSTREAM_LAYER_FOR from A to B. Layer order limits which dependencies are allowed. An observed dependency needs its own source evidence.

Package identification follows AN-S-3159. AN-S-2611 endpoint rules apply.
Unresolved bindings emit no Package edge; retain a trace to the source.

## Formal Manifest

```python anechoic-edsl
# Anechoic Python eDSL

from anechoic.model import Package, Relation

class Relation4866(Relation):
    name = 'IS_UPSTREAM_LAYER_FOR'
    relation.inverse_alias = 'IS_DOWNSTREAM_LAYER_FOR'
    relation.source_endpoint = {'level': 'instances', 'entity_paths': (Package,)}
    relation.target_endpoint = {'level': 'instances', 'entity_paths': (Package,)}
```
