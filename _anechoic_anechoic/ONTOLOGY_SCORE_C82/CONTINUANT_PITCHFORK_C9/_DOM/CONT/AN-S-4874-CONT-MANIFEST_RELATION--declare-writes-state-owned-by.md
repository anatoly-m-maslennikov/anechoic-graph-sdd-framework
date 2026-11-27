---
atom_family: SPEC
atom_id: AN-S-4874
concern:
  subject: WRITES_STATE_OWNED_BY
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
  updated_at: "2026-11-26T15:52:36.360336+00:00"
---

## Summary

Declare WRITES_STATE_OWNED_BY

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
