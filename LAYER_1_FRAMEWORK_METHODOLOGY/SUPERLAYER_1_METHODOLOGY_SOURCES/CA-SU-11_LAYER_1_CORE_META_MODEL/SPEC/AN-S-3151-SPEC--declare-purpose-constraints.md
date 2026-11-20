---
atom_family: SPEC
atom_id: AN-S-3151
structure:
  container:
    component: C9
context:
  lens: SPEC
state:
  status: active
  version: 1
  updated_at: '2026-11-20T14:42:07.157939+00:00'
---

## Summary

Declare Purpose Constraints

## Claim scope

MODEL//ANECHOIC <+ Node//Artifact//Atom//Spec Atom//Purpose.Constraints

## Claim

### Formal Claim

```python
from anechoic.formal_claims import declare_entity
from anechoic.model import Purpose

def check_purpose(purpose: Purpose) -> bool:
    return bool(purpose.purpose.strip())

declare_entity(
    entity_name='Purpose Constraints',
    constraints_for='Node//Artifact//Atom//Spec Atom//Purpose',
    instance_check=check_purpose,
)
```
