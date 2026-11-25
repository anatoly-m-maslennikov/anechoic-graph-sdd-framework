---
atom_family: SPEC
atom_id: AN-S-3313
container:
  component: C9
tier: 2
context:
  lens: SPEC
state:
  status: "archived"
  version: 1
  updated_at: '2026-11-21T18:17:21+00:00'
---

## Summary

Declare Project Contract Constraints

## Claim scope

MODEL//ANECHOIC <+ Node//Artifact//Atom//Spec Atom//Contract//Project Contract.Constraints

## Claim

### Formal Claim

```python
from anechoic.formal_claims import declare_entity
from anechoic.model import ProjectContract

declare_entity(
    entity_name='Project Contract Constraints',
    constraints_for='Node//Artifact//Atom//Spec Atom//Contract//Project Contract',
    instance_relation_constraints={'CONTAINED_BY': {'target_entity_paths': ('Node//Artifact//Component//Project',), 'targets_per_source': 1}},
)
```
