---
atom_family: SPEC
atom_id: AN-S-3153
structure:
  container:
    component: C9
context:
  lens: SPEC
state:
  status: archived
  version: 1
  updated_at: '2026-11-20T14:42:07.157939+00:00'
---

## Summary

Declare Component Purpose Constraints

## Claim scope

MODEL//ANECHOIC <+ Node//Artifact//Atom//Spec Atom//Purpose//Component Purpose.Constraints

## Claim

### Formal Claim

```python
from anechoic.formal_claims import declare_entity
from anechoic.model import ComponentPurpose

def check_component_purpose(purpose: ComponentPurpose) -> bool:
    return bool(purpose.component_id.strip())

declare_entity(
    entity_name='Component Purpose Constraints',
    constraints_for='Node//Artifact//Atom//Spec Atom//Purpose//Component Purpose',
    instance_relation_constraints={'CONTAINED_BY': {'target_entity_paths': ('Node//Artifact//Component',), 'targets_per_source': 1}},
    instance_check=check_component_purpose,
)
```
