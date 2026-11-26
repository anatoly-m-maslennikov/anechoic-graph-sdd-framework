---
atom_family: SPEC
atom_id: AN-S-3321
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

Declare REFINES

## Claim scope

MODEL//ANECHOIC <+ Relation//REFINES

## Claim

### Prose Claim

A Tier 2 Applicable Principle refines a Tier 1 Applicable Principle.
A Tier 4 Project SPEC Solution may refine a Tier 3 Project SPEC Solution.
The authored Relation points from the stated source to its target.
The inverse is derived. Tier and Solution restrictions are authoring rules.

### Formal Claim

```python
from anechoic.formal_claims import declare_relation

declare_relation(
    relation_name='REFINES',
    inverse_alias='IS_REFINED_BY',
    source_endpoint={'level': 'instances', 'entity_paths': ('Node//Artifact//Atom//Spec Atom',)},
    target_endpoint={'level': 'instances', 'entity_paths': ('Node//Artifact//Atom//Spec Atom',)},
    acyclic=True,
)
```
