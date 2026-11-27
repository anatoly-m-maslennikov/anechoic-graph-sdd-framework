---
atom_family: SPEC
atom_id: AN-S-4876
container:
  component: C9
tier: 2
context:
  lens: SPEC
  template: manifest_relation
state:
  status: "archived"
  version: 2
  updated_at: "2026-11-26T15:54:03.170501+00:00"
---

## Summary

Declare PUBLISHES_EVENTS_CONSUMED_BY

## Claim scope

MODEL//ANECHOIC <+ Graph/Relation//PUBLISHES_EVENTS_CONSUMED_BY

## Semantics

Relation type: Direct. Realization Graph edge facts are derived from source evidence.

Realization Graph evidence: a resolved publisher owned by Package A and consumer owned by Package B bind to the same channel and event type.
Direction: PUBLISHES_EVENTS_CONSUMED_BY from A to B.

Package identification follows AN-S-3159. AN-S-2611 endpoint rules apply.
Unresolved bindings emit no Package edge; retain a trace to the source.

## Formal Manifest

```python anechoic-edsl
# Anechoic Python eDSL

from anechoic.model import Package, Relation

class Relation4876(Relation):
    name = 'PUBLISHES_EVENTS_CONSUMED_BY'
    relation.inverse_alias = 'CONSUMES_EVENTS_PUBLISHED_BY'
    relation.source_endpoint = {'level': 'instances', 'entity_paths': (Package,)}
    relation.target_endpoint = {'level': 'instances', 'entity_paths': (Package,)}
```
