---
atom_family: SPEC
atom_id: AN-S-4875
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

Declare HAS_STATE_WRITER

## Claim scope

MODEL//ANECHOIC <+ Graph/Relation//HAS_STATE_WRITER

## Semantics

Derivation: Derived.

Realization Graph evidence: Package A owns a resolved resource written by Package B.
Direction: HAS_STATE_WRITER from A to B. Paired name from the same evidence: WRITES_STATE_OWNED_BY from B to A.

Both endpoints are Package instances identified under AN-S-3159; AN-S-2611 endpoint rules apply.
Unresolved bindings emit no Package edge; retain a trace to the source.

## Formal Manifest

```python anechoic-edsl
# Anechoic Python eDSL

from anechoic.model import Package, Relation

class Relation4875(Relation):
    name = 'HAS_STATE_WRITER'
    source_endpoint = {'level': 'instances', 'entity_paths': (Package,)}
    target_endpoint = {'level': 'instances', 'entity_paths': (Package,)}
```
