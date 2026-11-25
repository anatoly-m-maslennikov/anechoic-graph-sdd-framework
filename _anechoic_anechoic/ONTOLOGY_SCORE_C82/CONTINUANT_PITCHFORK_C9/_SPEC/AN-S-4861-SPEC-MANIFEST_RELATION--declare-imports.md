---
atom_family: SPEC
atom_id: AN-S-4861
container:
  component: C9
tier: 2
context:
  lens: SPEC
  template: manifest_relation
state:
  status: "active"
  version: 2
  updated_at: "2026-11-25T16:00:38.228664+00:00"
---

## Summary

Declare IMPORTS

## Claim scope

MODEL//ANECHOIC <+ Graph/Relation//IMPORTS

## Semantics

Relation type: Direct. Realization Graph edge facts are derived from source evidence.

Realization Graph evidence: Package A has a resolved import occurrence whose immediate ownership identifies Package A and Package B, per AN-S-3085.
Direction: IMPORTS from A to B. Intra-Package imports remain visible.

Package identification follows AN-S-3159. AN-S-2611 endpoint rules apply.
Unresolved bindings emit no Package edge; retain a trace to the source.

## Formal Manifest

```python anechoic-edsl
# Anechoic Python eDSL

from anechoic.model import Package, Relation

class Relation4861(Relation):
    name = 'IMPORTS'
    relation.inverse_alias = 'IS_IMPORTED_BY'
    relation.source_endpoint = {'level': 'instances', 'entity_paths': (Package,)}
    relation.target_endpoint = {'level': 'instances', 'entity_paths': (Package,)}
```
