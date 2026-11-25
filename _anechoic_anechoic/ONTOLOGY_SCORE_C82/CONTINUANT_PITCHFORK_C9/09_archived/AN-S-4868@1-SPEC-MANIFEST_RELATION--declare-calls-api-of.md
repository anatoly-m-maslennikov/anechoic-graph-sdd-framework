---
atom_family: SPEC
atom_id: AN-S-4868
container:
  component: C9
tier: 2
context:
  lens: SPEC
  template: manifest_relation
state:
  status: "archived"
  version: 1
  updated_at: "2026-11-25T10:51:30.781749+00:00"
---

## Summary

Declare CALLS_API_OF

## Claim scope

MODEL//ANECHOIC <+ Graph/Relation//CALLS_API_OF

## Semantics

Relation type: Direct. Realization Graph edge facts are derived from source evidence.

Realization Graph evidence: a resolved client in Package A calls an operation owned by Package B.
Direction: CALLS_API_OF from A to B. The inverse alias reverses this view: HAS_API_CALLER from B to A.

Both endpoints are Package instances identified under AN-S-3159; AN-S-2611 endpoint rules apply.
Unresolved bindings emit no Package edge; retain a trace to the source.

## Formal Manifest

```python anechoic-edsl
# Anechoic Python eDSL

from anechoic.model import Package, Relation

class Relation4868(Relation):
    name = 'CALLS_API_OF'
    inverse_alias = 'HAS_API_CALLER'
    source_endpoint = {'level': 'instances', 'entity_paths': (Package,)}
    target_endpoint = {'level': 'instances', 'entity_paths': (Package,)}
```
