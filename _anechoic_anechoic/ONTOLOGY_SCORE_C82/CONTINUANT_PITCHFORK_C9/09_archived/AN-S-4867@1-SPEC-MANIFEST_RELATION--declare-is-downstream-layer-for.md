---
atom_family: SPEC
atom_id: AN-S-4867
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

Declare IS_DOWNSTREAM_LAYER_FOR

## Claim scope

MODEL//ANECHOIC <+ Graph/Relation//IS_DOWNSTREAM_LAYER_FOR

## Semantics

Derivation: Derived.

Realization Graph evidence: Package A and Package B are in the same ordered sibling group, and A has the higher layer number.
Direction: IS_DOWNSTREAM_LAYER_FOR from A to B. Paired name from the same evidence: IS_UPSTREAM_LAYER_FOR from B to A.

Both endpoints are Package instances identified under AN-S-3159; AN-S-2611 endpoint rules apply.
Unresolved bindings emit no Package edge; retain a trace to the source.

## Formal Manifest

```python anechoic-edsl
# Anechoic Python eDSL

from anechoic.model import Package, Relation

class Relation4867(Relation):
    name = 'IS_DOWNSTREAM_LAYER_FOR'
    source_endpoint = {'level': 'instances', 'entity_paths': (Package,)}
    target_endpoint = {'level': 'instances', 'entity_paths': (Package,)}
```
