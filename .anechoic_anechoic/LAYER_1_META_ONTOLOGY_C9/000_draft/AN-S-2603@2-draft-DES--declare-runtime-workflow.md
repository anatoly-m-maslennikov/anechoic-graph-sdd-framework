---
identity:
  atom_id: AN-S-2603
context:
  container:
    component: C9
  tier: 3
  lens: DES
state:
  status: draft
  version: 2
  updated_at: 2026-11-11 14:06:22 +0400
---

## Summary

Declare Runtime Workflow

## Claim

### Formal Claim

```python
# model
allowed_values(address='Atom/(.Header.Context.Role in (Operations))/Workflow.Purpose', values=('Runtime',))
subject_path(address='Atom/(.Header.Context.Role in (Operations))/Workflow/(.Purpose in (Runtime))')
```

## Semantics

A Runtime Workflow provides behavior through a Project’s delivered result during its operation.
