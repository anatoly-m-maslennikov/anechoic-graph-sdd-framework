---
atom_family: SPEC
atom_id: AN-S-3323
container:
  component: C9
tier: 2
context:
  lens: SPEC
state:
  status: active
  version: 2
  updated_at: '2026-11-22T22:23:08.810817+00:00'
---

## Summary

Declare IS_SOLUTION_FOR

## Claim scope

MODEL//ANECHOIC <+ Relation//IS_SOLUTION_FOR

## Claim

### Prose Claim

A Tier 1 SPEC Atom is a solution for a Tier 0 Contract when its claim
describes how to meet a specific guarantee in that Contract. Any Tier 1
SPEC Template can play this role. The authored Relation points from the
Tier 1 Atom to the Contract. Derive HAS_SOLUTION for the same direct
pair. The tier and guarantee rules are authoring rules.

### Formal Claim

```python
from anechoic.formal_claims import declare_relation

declare_relation(
    relation_name='IS_SOLUTION_FOR',
    inverse_alias='HAS_SOLUTION',
    source_endpoint={'level': 'instances', 'entity_paths': ('Node//Artifact//Atom//Spec Atom',)},
    target_endpoint={'level': 'instances', 'entity_paths': ('Node//Artifact//Atom//Spec Atom//Contract',)},
)
```
