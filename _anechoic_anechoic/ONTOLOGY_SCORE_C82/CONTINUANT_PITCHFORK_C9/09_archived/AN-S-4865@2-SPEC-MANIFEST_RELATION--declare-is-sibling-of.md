---
atom_family: SPEC
atom_id: AN-S-4865
container:
  component: C9
tier: 2
context:
  lens: SPEC
  template: manifest_relation
state:
  status: "archived"
  version: 2
  updated_at: "2026-11-26T15:54:03.107396+00:00"
---

## Summary

Declare IS_SIBLING_OF

## Claim scope

MODEL//ANECHOIC <+ Graph/Relation//IS_SIBLING_OF

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
