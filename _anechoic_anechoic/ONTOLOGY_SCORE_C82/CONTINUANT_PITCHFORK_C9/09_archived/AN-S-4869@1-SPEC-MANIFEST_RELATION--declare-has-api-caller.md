---
atom_family: SPEC
atom_id: AN-S-4869
container:
  component: C9
tier: 2
context:
  lens: SPEC
  template: manifest_relation
state:
  status: archived
  version: 1
  updated_at: '2026-11-24T22:29:15+00:00'
---

## Summary

Declare HAS_API_CALLER

## Claim scope

MODEL//ANECHOIC <+ Graph/Relation//HAS_API_CALLER

## Semantics

Derivation: Derived.

Realization Graph evidence: Package A owns an operation called by a resolved client in Package B.
Direction: HAS_API_CALLER from A to B. Paired name from the same evidence: CALLS_API_OF from B to A.

Both endpoints are Package instances identified under AN-S-3159; AN-S-2611 endpoint rules apply.
Unresolved bindings emit no Package edge; retain a trace to the source.

## Formal Manifest

```python anechoic-edsl
# Anechoic Python eDSL

from anechoic.model import Package, Relation

class Relation4869(Relation):
    name = 'HAS_API_CALLER'
    source_endpoint = {'level': 'instances', 'entity_paths': (Package,)}
    target_endpoint = {'level': 'instances', 'entity_paths': (Package,)}
```
