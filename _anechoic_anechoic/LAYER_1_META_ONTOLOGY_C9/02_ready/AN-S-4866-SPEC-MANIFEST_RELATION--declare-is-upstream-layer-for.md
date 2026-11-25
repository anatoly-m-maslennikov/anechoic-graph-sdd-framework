---
atom_family: SPEC
atom_id: AN-S-4866
container:
  component: C9
tier: 2
context:
  lens: SPEC
  template: manifest_relation
state:
  status: "ready"
  version: 1
  updated_at: "2026-11-25T01:27:52.208132+00:00"
---

## Summary

Declare IS_UPSTREAM_LAYER_FOR

## Claim scope

MODEL//ANECHOIC <+ Relation//IS_UPSTREAM_LAYER_FOR

## Claim

### Prose Claim

Relation type: Direct. Realization Graph edge facts are derived from source evidence.

Realization Graph evidence: Package A and Package B are in the same ordered sibling group, and A has the lower layer number.
Direction: IS_UPSTREAM_LAYER_FOR from A to B. The inverse alias reverses this view: IS_DOWNSTREAM_LAYER_FOR from B to A.

Both endpoints are Package instances identified under AN-S-3159; AN-S-2611 endpoint rules apply.
Unresolved bindings emit no Package edge; retain a trace to the source.

### Formal Claim

```python
from anechoic.formal_claims import declare_relation

declare_relation(
    relation_name='IS_UPSTREAM_LAYER_FOR',
    inverse_alias='IS_DOWNSTREAM_LAYER_FOR',
    source_endpoint={'level': 'instances', 'entity_paths': ('Node//Artifact//Package',)},
    target_endpoint={'level': 'instances', 'entity_paths': ('Node//Artifact//Package',)},
)
```
