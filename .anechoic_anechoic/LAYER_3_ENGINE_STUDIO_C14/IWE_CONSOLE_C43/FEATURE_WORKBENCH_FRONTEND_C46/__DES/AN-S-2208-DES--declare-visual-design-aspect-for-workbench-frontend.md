---
atom_family: SPEC
atom_id: AN-S-2208
structure:
  container:
    component: C46
  tier: 4
context:
  lens: DES
state:
  status: active
  version: 4
  updated_at: '2026-11-13T05:19:37.263532+00:00'
---
## Summary

Declare Visual Design Aspect for Workbench Frontend

## Claim

### Prose Claim

WORKBENCH_FRONTEND uses Visual Design as a project-local Aspect.

### Formal Claim

```python
# project_structure
composition(container="PROJECT STRUCTURE//ANECHOIC", parts=("Aspect//Visual Design",))
```

## Semantics

Visual Design covers Operator presentation, not query semantics, source authority or backend behavior.
