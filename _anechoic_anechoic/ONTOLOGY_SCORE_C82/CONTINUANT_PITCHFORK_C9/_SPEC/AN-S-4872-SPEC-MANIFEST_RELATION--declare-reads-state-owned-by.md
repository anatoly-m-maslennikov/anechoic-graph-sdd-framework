---
atom_family: SPEC
atom_id: AN-S-4872
container:
  component: C9
tier: 2
context:
  lens: SPEC
  template: manifest_relation
state:
  status: "active"
  version: 2
  updated_at: "2026-11-25T16:00:38.267631+00:00"
---

## Summary

Declare READS_STATE_OWNED_BY

## Claim scope

MODEL//ANECHOIC <+ Graph/Relation//READS_STATE_OWNED_BY

## Semantics

Relation type: Direct. Realization Graph edge facts are derived from source evidence.

Realization Graph evidence: Package A reads a resolved resource designated as owned by Package B.
Direction: READS_STATE_OWNED_BY from A to B.

Package identification follows AN-S-3159. AN-S-2611 endpoint rules apply.
Unresolved bindings emit no Package edge; retain a trace to the source.

## Formal Manifest

```python anechoic-edsl
# Anechoic Python eDSL

from anechoic.model import Package, Relation

class Relation4872(Relation):
    name = 'READS_STATE_OWNED_BY'
    relation.inverse_alias = 'HAS_STATE_READER'
    relation.source_endpoint = {'level': 'instances', 'entity_paths': (Package,)}
    relation.target_endpoint = {'level': 'instances', 'entity_paths': (Package,)}
```
