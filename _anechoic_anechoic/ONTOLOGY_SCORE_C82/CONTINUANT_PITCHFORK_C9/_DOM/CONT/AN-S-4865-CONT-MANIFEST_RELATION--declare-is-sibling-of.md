---
atom_family: SPEC
atom_id: AN-S-4865
concern:
  subject: IS_SIBLING_OF
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
  version: 3
  updated_at: "2026-11-26T15:52:36.107001+00:00"
---

## Summary

Declare IS_SIBLING_OF

## Semantics

Relation type: Direct. Realization Graph edge facts are derived from source evidence.

Realization Graph evidence: distinct Package A and Package B have the same immediate structural parent.
Projection rule: emit IS_SIBLING_OF in both directions from the shared parent evidence. Emit no self-pairs. This Relation has no inverse alias.

Package identification follows AN-S-3159. AN-S-2611 endpoint rules apply.
Unresolved bindings emit no Package edge; retain a trace to the source.

## Formal Manifest

```python anechoic-edsl
# Anechoic Python eDSL

from anechoic.model import Package, Relation

class Relation4865(Relation):
    name = 'IS_SIBLING_OF'
    relation.source_endpoint = {'level': 'instances', 'entity_paths': (Package,)}
    relation.target_endpoint = {'level': 'instances', 'entity_paths': (Package,)}
```
