---
atom_family: SPEC
atom_id: AN-S-4872
container:
  component: C9
tier: 2
context:
  lens: SPEC
  template: manifest_relation
state:
  status: "ready"
  version: 1
  updated_at: "2026-11-25T01:27:56.263940+00:00"
---

## Summary

Declare READS_STATE_OWNED_BY

## Claim scope

MODEL//ANECHOIC <+ Relation//READS_STATE_OWNED_BY

## Claim

### Prose Claim

Relation type: Direct. Realization Graph edge facts are derived from source evidence.

Realization Graph evidence: Package A reads a resolved resource designated as owned by Package B.
Direction: READS_STATE_OWNED_BY from A to B. The inverse alias reverses this view: HAS_STATE_READER from B to A.

Both endpoints are Package instances identified under AN-S-3159; AN-S-2611 endpoint rules apply.
Unresolved bindings emit no Package edge; retain a trace to the source.

### Formal Claim

```python
from anechoic.formal_claims import declare_relation

declare_relation(
    relation_name='READS_STATE_OWNED_BY',
    inverse_alias='HAS_STATE_READER',
    source_endpoint={'level': 'instances', 'entity_paths': ('Node//Artifact//Package',)},
    target_endpoint={'level': 'instances', 'entity_paths': ('Node//Artifact//Package',)},
)
```
