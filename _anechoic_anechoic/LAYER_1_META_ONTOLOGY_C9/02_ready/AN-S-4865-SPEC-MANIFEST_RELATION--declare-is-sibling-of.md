---
atom_family: SPEC
atom_id: AN-S-4865
container:
  component: C9
tier: 2
context:
  lens: SPEC
  template: manifest_relation
state:
  status: "ready"
  version: 1
  updated_at: "2026-11-25T01:27:50.307858+00:00"
---

## Summary

Declare IS_SIBLING_OF

## Claim scope

MODEL//ANECHOIC <+ Relation//IS_SIBLING_OF

## Claim

### Prose Claim

Relation type: Direct. Realization Graph edge facts are derived from source evidence.

Realization Graph evidence: distinct Package A and Package B have the same immediate structural parent.
Projection rule: emit IS_SIBLING_OF in both directions from the shared parent evidence. Emit no self-pairs. This Relation has no inverse alias.

Both endpoints are Package instances identified under AN-S-3159; AN-S-2611 endpoint rules apply.
Unresolved bindings emit no Package edge; retain a trace to the source.

### Formal Claim

```python
from anechoic.formal_claims import declare_relation

declare_relation(
    relation_name='IS_SIBLING_OF',
    source_endpoint={'level': 'instances', 'entity_paths': ('Node//Artifact//Package',)},
    target_endpoint={'level': 'instances', 'entity_paths': ('Node//Artifact//Package',)},
)
```
