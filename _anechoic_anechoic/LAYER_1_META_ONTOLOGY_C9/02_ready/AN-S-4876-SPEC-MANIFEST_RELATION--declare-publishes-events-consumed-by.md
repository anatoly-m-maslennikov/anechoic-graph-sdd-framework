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
  status: "ready"
  version: 1
  updated_at: "2026-11-25T01:27:58.990341+00:00"
---

## Summary

Declare PUBLISHES_EVENTS_CONSUMED_BY

## Claim scope

MODEL//ANECHOIC <+ Relation//PUBLISHES_EVENTS_CONSUMED_BY

## Claim

### Prose Claim

Relation type: Direct. Realization Graph edge facts are derived from source evidence.

Realization Graph evidence: a resolved publisher owned by Package A and consumer owned by Package B bind to the same channel and event type.
Direction: PUBLISHES_EVENTS_CONSUMED_BY from A to B. The inverse alias reverses this view: CONSUMES_EVENTS_PUBLISHED_BY from B to A.

Both endpoints are Package instances identified under AN-S-3159; AN-S-2611 endpoint rules apply.
Unresolved bindings emit no Package edge; retain a trace to the source.

### Formal Claim

```python
from anechoic.formal_claims import declare_relation

declare_relation(
    relation_name='PUBLISHES_EVENTS_CONSUMED_BY',
    inverse_alias='CONSUMES_EVENTS_PUBLISHED_BY',
    source_endpoint={'level': 'instances', 'entity_paths': ('Node//Artifact//Package',)},
    target_endpoint={'level': 'instances', 'entity_paths': ('Node//Artifact//Package',)},
)
```
