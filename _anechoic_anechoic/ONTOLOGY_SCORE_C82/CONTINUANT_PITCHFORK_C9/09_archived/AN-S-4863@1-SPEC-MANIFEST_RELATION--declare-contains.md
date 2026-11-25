---
atom_family: SPEC
atom_id: AN-S-4863
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

Declare CONTAINS

## Claim scope

MODEL//ANECHOIC <+ Graph/Relation//CONTAINS

## Semantics

Derivation: Derived.

Realization Graph evidence: the Package projection admits Package B as an immediate structural member of Package A.
Direction: CONTAINS from A to B. Paired name from the same evidence: CONTAINED_BY from B to A. AN-S-2715 defines this Package containment meaning.

Both endpoints are Package instances identified under AN-S-3159; AN-S-2611 endpoint rules apply.
Unresolved bindings emit no Package edge; retain a trace to the source.

## Formal Manifest

```python anechoic-edsl
# Anechoic Python eDSL

from anechoic.model import Package, Relation

class Relation4863(Relation):
    name = 'CONTAINS'
    source_endpoint = {'level': 'instances', 'entity_paths': (Package,)}
    target_endpoint = {'level': 'instances', 'entity_paths': (Package,)}
```
