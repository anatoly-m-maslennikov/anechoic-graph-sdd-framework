---
atom_family: SPEC
atom_id: AN-S-4864
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

Declare CONTAINED_BY

## Claim scope

MODEL//ANECHOIC <+ Graph/Relation//CONTAINED_BY

## Semantics

Derivation: Derived.

Realization Graph evidence: the Package projection admits Package A as an immediate structural member of Package B.
Direction: CONTAINED_BY from A to B. Paired name from the same evidence: CONTAINS from B to A. AN-S-2715 defines this Package containment meaning.

Both endpoints are Package instances identified under AN-S-3159; AN-S-2611 endpoint rules apply.
Unresolved bindings emit no Package edge; retain a trace to the source.

## Formal Manifest

```python anechoic-edsl
# Anechoic Python eDSL

from anechoic.model import Package, Relation

class Relation4864(Relation):
    name = 'CONTAINED_BY'
    source_endpoint = {'level': 'instances', 'entity_paths': (Package,)}
    target_endpoint = {'level': 'instances', 'entity_paths': (Package,)}
```
