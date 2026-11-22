---
atom_family: SPEC
atom_id: AN-S-3148
container:
  component: C9
tier: 2
context:
  lens: SPEC
state:
  status: active
  version: 1
  updated_at: '2026-11-20T14:42:07.157939+00:00'
---

## Summary

Declare Component Constraints

## Claim scope

MODEL//ANECHOIC <+ Node//Artifact//Component.Constraints

## Claim

### Formal Claim

```python
from anechoic.formal_claims import declare_entity
from anechoic.model import Component

declare_entity(
    entity_name='Component Constraints',
    constraints_for='Node//Artifact//Component',
    instance_relation_constraints={'CHILD_OF': {'target_entity_paths': ('Node//Artifact//Component',), 'targets_per_source': 1}},
)
```
