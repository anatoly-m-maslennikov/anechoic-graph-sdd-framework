---
atom_family: SPEC
atom_id: AN-S-4870
container:
  component: C9
tier: 2
context:
  lens: SPEC
  template: manifest_relation
state:
  status: "ready"
  version: 1
  updated_at: "2026-11-25T01:27:55.015117+00:00"
---

## Summary

Declare STARTS_PROCESS_OF

## Claim scope

MODEL//ANECHOIC <+ Relation//STARTS_PROCESS_OF

## Claim

### Prose Claim

Relation type: Direct. Realization Graph edge facts are derived from source evidence.

Realization Graph evidence: a launch site owned by Package A resolves to an entry point owned by Package B.
Direction: STARTS_PROCESS_OF from A to B. The inverse alias reverses this view: HAS_PROCESS_STARTED_BY from B to A.

Both endpoints are Package instances identified under AN-S-3159; AN-S-2611 endpoint rules apply.
Unresolved bindings emit no Package edge; retain a trace to the source.

### Formal Claim

```python
from anechoic.formal_claims import declare_relation

declare_relation(
    relation_name='STARTS_PROCESS_OF',
    inverse_alias='HAS_PROCESS_STARTED_BY',
    source_endpoint={'level': 'instances', 'entity_paths': ('Node//Artifact//Package',)},
    target_endpoint={'level': 'instances', 'entity_paths': ('Node//Artifact//Package',)},
)
```
