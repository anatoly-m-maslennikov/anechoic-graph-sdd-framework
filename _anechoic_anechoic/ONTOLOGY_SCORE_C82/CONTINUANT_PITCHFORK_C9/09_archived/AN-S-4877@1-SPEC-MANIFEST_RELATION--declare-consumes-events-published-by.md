---
atom_family: SPEC
atom_id: AN-S-4877
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

Declare CONSUMES_EVENTS_PUBLISHED_BY

## Claim scope

MODEL//ANECHOIC <+ Graph/Relation//CONSUMES_EVENTS_PUBLISHED_BY

## Semantics

Derivation: Derived.

Realization Graph evidence: a resolved consumer owned by Package A and publisher owned by Package B bind to the same channel and event type.
Direction: CONSUMES_EVENTS_PUBLISHED_BY from A to B. Paired name from the same evidence: PUBLISHES_EVENTS_CONSUMED_BY from B to A.

Both endpoints are Package instances identified under AN-S-3159; AN-S-2611 endpoint rules apply.
Unresolved bindings emit no Package edge; retain a trace to the source.

## Formal Manifest

```python anechoic-edsl
# Anechoic Python eDSL

from anechoic.model import Package, Relation

class Relation4877(Relation):
    name = 'CONSUMES_EVENTS_PUBLISHED_BY'
    source_endpoint = {'level': 'instances', 'entity_paths': (Package,)}
    target_endpoint = {'level': 'instances', 'entity_paths': (Package,)}
```
