---
atom_family: SPEC
atom_id: AN-S-3111
container:
  component: C9
tier: 2
context:
  lens: SPEC
state:
  status: archived
  version: 1
  updated_at: '2026-11-20T11:17:59+00:00'
---

## Summary

Declare Project Goal

## Claim scope

MODEL//ANECHOIC <+ Node//Artifact//Atom//Spec Atom//Purpose//Project Goal

## Claim

### Formal Claim

```python
from anechoic.formal_claims import declare_entity
from anechoic.model import Purpose
from dataclasses import field

class ProjectGoal(Purpose):
    tier: int = field(metadata={"allowed_values": (-1,)})

declare_entity(
    entity_name="Project Goal",
    entity_class=ProjectGoal,
    instance_relation_constraints={
        "CONTAINED_BY": {"target_entity_paths": ("Node//Artifact//Component//Project",), "targets_per_source": 1},
    },
)
```
