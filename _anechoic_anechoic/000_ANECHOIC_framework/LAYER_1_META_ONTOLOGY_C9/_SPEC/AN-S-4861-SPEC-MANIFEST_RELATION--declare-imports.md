---
atom_family: SPEC
atom_id: AN-S-4861
container:
  component: C9
tier: 2
context:
  lens: SPEC
  template: manifest_relation
state:
  status: "active"
  version: 1
  updated_at: "2026-11-25T01:36:28.441617+00:00"
---

## Summary

Declare IMPORTS

## Claim scope

MODEL//ANECHOIC <+ Relation//IMPORTS

## Claim

### Prose Claim

Relation type: Direct. Realization Graph edge facts are derived from source evidence.

Realization Graph evidence: Package A has a resolved import occurrence whose immediate ownership identifies Package A and Package B, per AN-S-3085.
Direction: IMPORTS from A to B. The inverse alias reverses this view: IS_IMPORTED_BY from B to A. Intra-Package imports remain visible.

Both endpoints are Package instances identified under AN-S-3159; AN-S-2611 endpoint rules apply.
Unresolved bindings emit no Package edge; retain a trace to the source.

### Formal Claim

```python
from anechoic.formal_claims import declare_relation

declare_relation(
    relation_name='IMPORTS',
    inverse_alias='IS_IMPORTED_BY',
    source_endpoint={'level': 'instances', 'entity_paths': ('Node//Artifact//Package',)},
    target_endpoint={'level': 'instances', 'entity_paths': ('Node//Artifact//Package',)},
)
```
