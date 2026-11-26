---
atom_family: SPEC
atom_id: AN-S-3323
container:
  component: C9
tier: 2
context:
  lens: SPEC
state:
  status: archived
  version: 1
  updated_at: '2026-11-22T00:00:00+00:00'
---

## Summary

Declare IS_SOLUTION_FOR

## Claim scope

MODEL//ANECHOIC <+ Relation//IS_SOLUTION_FOR

## Claim

### Prose Claim

A Tier 3 Project SPEC Solution is a solution for a Tier 0 Project Contract.
The authored Relation points from the stated source to its target.
The inverse is derived. Tier and Solution restrictions are authoring rules.

### Formal Claim

```python
from anechoic.formal_claims import declare_relation

declare_relation(
    relation_name='IS_SOLUTION_FOR',
    inverse_alias='HAS_SOLUTION',
    source_endpoint={'level': 'instances', 'entity_paths': ('Node//Artifact//Atom//Spec Atom',)},
    target_endpoint={'level': 'instances', 'entity_paths': ('Node//Artifact//Atom//Spec Atom//Contract//Project Contract',)},
)
```
