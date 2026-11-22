---
atom_family: SPEC
atom_id: AN-S-3319
container:
  component: C9
tier: 2
context:
  lens: SPEC
state:
  status: active
  version: 2
  updated_at: '2026-11-22T11:49:27.339015+00:00'
---

## Summary

Declare APPLIES

## Claim scope

MODEL//ANECHOIC <+ Relation//APPLIES

## Claim

### Prose Claim

A Tier 1 Applicable Principle applies a Tier 0 Axiom as a premise
within the scope of its Project Goal.
The authored Relation points from the stated source to its target.
The inverse is derived. Tier and Solution restrictions are authoring rules.

### Formal Claim

```python
from anechoic.formal_claims import declare_relation

declare_relation(
    relation_name='APPLIES',
    inverse_alias='IS_APPLIED_BY',
    source_endpoint={'level': 'instances', 'entity_paths': ('Node//Artifact//Atom//Spec Atom//Applicable Principle',)},
    target_endpoint={'level': 'instances', 'entity_paths': ('Node//Artifact//Atom//Spec Atom//Axiom',)},
)
```
