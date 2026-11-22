---
atom_family: SPEC
atom_id: AN-S-3322
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

Declare CONTRIBUTES_TO

## Claim scope

MODEL//ANECHOIC <+ Relation//CONTRIBUTES_TO

## Claim

### Prose Claim

A Tier 2 Applicable Principle contributes to a Tier 1 Applicable Principle
when it supports the Principle without refining it. A Tier 3 Project SPEC
Solution, Policy, or Standard may contribute to a Tier 2 Applicable Principle.
The authored Relation points from the stated source to its target.
The inverse is derived. Tier and Solution restrictions are authoring rules.

### Formal Claim

```python
from anechoic.formal_claims import declare_relation

declare_relation(
    relation_name='CONTRIBUTES_TO',
    inverse_alias='RECEIVES_CONTRIBUTION_FROM',
    source_endpoint={'level': 'instances', 'entity_paths': ('Node//Artifact//Atom//Spec Atom',)},
    target_endpoint={'level': 'instances', 'entity_paths': ('Node//Artifact//Atom//Spec Atom//Applicable Principle',)},
)
```
