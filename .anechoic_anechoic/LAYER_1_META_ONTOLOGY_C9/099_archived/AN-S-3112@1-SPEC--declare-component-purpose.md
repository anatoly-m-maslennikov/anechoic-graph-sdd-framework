---
atom_family: SPEC
atom_id: AN-S-3112
structure:
  container:
    component: C9
context:
  lens: SPEC
state:
  status: archived
  version: 1
  updated_at: '2026-11-20T11:17:59+00:00'
---

## Summary

Declare Component Purpose

## Claim scope

MODEL//ANECHOIC <+ Node//Artifact//Atom//Spec Atom//Purpose//Component Purpose

## Claim

### Formal Claim

```python
from anechoic.formal_claims import declare_entity
from anechoic.model import Purpose
from dataclasses import field

class ComponentPurpose(Purpose):
    tier: int = field(metadata={"allowed_values": (0,)})
    component_id: str

def check_component_purpose(purpose: ComponentPurpose) -> bool:
    return bool(purpose.component_id.strip())

declare_entity(
    entity_name="Component Purpose",
    entity_class=ComponentPurpose,
    instance_relation_constraints={
        "CONTAINED_BY": {"target_entity_paths": ("Node//Artifact//Component",), "targets_per_source": 1},
    },
    instance_check=check_component_purpose,
)
```
