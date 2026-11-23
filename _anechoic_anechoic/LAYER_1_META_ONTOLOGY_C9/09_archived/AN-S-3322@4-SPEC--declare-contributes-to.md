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
  version: 4
  updated_at: '2026-11-22T11:34:35.965837+00:00'
---

## Summary

Declare CONTRIBUTES_TO

## Claim scope

MODEL//ANECHOIC <+ Relation//CONTRIBUTES_TO

## Claim

### Prose Claim

An Atom contributes when it supplies guidance or part of the design needed
to put the target claim into practice. Use this Relation in the Project for:

- Tier 2 Applicable Principle to Tier 1 Applicable Principle.
- Tier 3 Solution, Policy, or Standard to Tier 2 Applicable Principle.
- Tier 4 Solution or Component Manifest to Tier 3 Solution.
The authored Relation points from the stated source to its target.
The inverse is derived. Tier and Solution restrictions are authoring rules.

### Formal Claim

```python
from anechoic.formal_claims import declare_relation

declare_relation(
    relation_name='CONTRIBUTES_TO',
    inverse_alias='RECEIVES_CONTRIBUTION_FROM',
    source_endpoint={'level': 'instances', 'entity_paths': ('Node//Artifact//Atom//Spec Atom',)},
    target_endpoint={'level': 'instances', 'entity_paths': ('Node//Artifact//Atom//Spec Atom',)},
)
```
