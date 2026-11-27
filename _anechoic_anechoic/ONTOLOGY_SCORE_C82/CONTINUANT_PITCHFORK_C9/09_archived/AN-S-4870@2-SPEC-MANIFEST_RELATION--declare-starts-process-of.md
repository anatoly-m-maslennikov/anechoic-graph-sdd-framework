---
atom_family: SPEC
atom_id: AN-S-4870
container:
  component: C9
tier: 2
context:
  lens: SPEC
  template: manifest_relation
state:
  status: "archived"
  version: 2
  updated_at: "2026-11-26T15:54:03.148978+00:00"
---

## Summary

Declare STARTS_PROCESS_OF

## Claim scope

MODEL//ANECHOIC <+ Graph/Relation//STARTS_PROCESS_OF

## Semantics

Relation type: Direct. Realization Graph edge facts are derived from source evidence.

Realization Graph evidence: a launch site owned by Package A resolves to an entry point owned by Package B.
Direction: STARTS_PROCESS_OF from A to B.

Package identification follows AN-S-3159. AN-S-2611 endpoint rules apply.
Unresolved bindings emit no Package edge; retain a trace to the source.

## Formal Manifest

```python anechoic-edsl
# Anechoic Python eDSL

from anechoic.model import Package, Relation

class Relation4870(Relation):
    name = 'STARTS_PROCESS_OF'
    relation.inverse_alias = 'HAS_PROCESS_STARTED_BY'
    relation.source_endpoint = {'level': 'instances', 'entity_paths': (Package,)}
    relation.target_endpoint = {'level': 'instances', 'entity_paths': (Package,)}
```
