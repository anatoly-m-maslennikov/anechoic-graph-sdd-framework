---
atom_family: SPEC
atom_id: AN-S-4866
concern:
  subject: IS_UPSTREAM_LAYER_FOR
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
  version: 4
  updated_at: "2026-11-26T15:52:36.147756+00:00"
---

## Summary

Declare IS_UPSTREAM_LAYER_FOR

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
