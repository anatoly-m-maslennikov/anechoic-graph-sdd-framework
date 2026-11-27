---
atom_family: SPEC
atom_id: AN-S-4874
container:
  component: C9
tier: 2
context:
  lens: SPEC
  template: manifest_relation
state:
  status: "archived"
  version: 2
  updated_at: "2026-11-26T15:54:03.163450+00:00"
---

## Summary

Declare WRITES_STATE_OWNED_BY

## Claim scope

MODEL//ANECHOIC <+ Graph/Relation//WRITES_STATE_OWNED_BY

## Semantics

Relation type: Direct. Realization Graph edge facts are derived from source evidence.

Realization Graph evidence: Package A writes a resolved resource designated as owned by Package B.
Direction: WRITES_STATE_OWNED_BY from A to B.

Package identification follows AN-S-3159. AN-S-2611 endpoint rules apply.
Unresolved bindings emit no Package edge; retain a trace to the source.

## Formal Manifest

```python anechoic-edsl
# Anechoic Python eDSL

from anechoic.model import Package, Relation

class Relation4874(Relation):
    name = 'WRITES_STATE_OWNED_BY'
    relation.inverse_alias = 'HAS_STATE_WRITER'
    relation.source_endpoint = {'level': 'instances', 'entity_paths': (Package,)}
    relation.target_endpoint = {'level': 'instances', 'entity_paths': (Package,)}
```
