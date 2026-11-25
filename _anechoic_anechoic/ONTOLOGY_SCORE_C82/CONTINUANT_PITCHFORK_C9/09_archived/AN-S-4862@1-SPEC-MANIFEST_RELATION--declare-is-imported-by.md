---
atom_family: SPEC
atom_id: AN-S-4862
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

Declare IS_IMPORTED_BY

## Claim scope

MODEL//ANECHOIC <+ Graph/Relation//IS_IMPORTED_BY

## Semantics

Derivation: Derived.

Realization Graph evidence: Package B has a resolved import occurrence whose immediate ownership identifies Package B and Package A, per AN-S-3085.
Direction: IS_IMPORTED_BY from A to B. Paired name from the same evidence: IMPORTS from B to A. Intra-Package imports remain visible.

Both endpoints are Package instances identified under AN-S-3159; AN-S-2611 endpoint rules apply.
Unresolved bindings emit no Package edge; retain a trace to the source.

## Formal Manifest

```python anechoic-edsl
# Anechoic Python eDSL

from anechoic.model import Package, Relation

class Relation4862(Relation):
    name = 'IS_IMPORTED_BY'
    source_endpoint = {'level': 'instances', 'entity_paths': (Package,)}
    target_endpoint = {'level': 'instances', 'entity_paths': (Package,)}
```
