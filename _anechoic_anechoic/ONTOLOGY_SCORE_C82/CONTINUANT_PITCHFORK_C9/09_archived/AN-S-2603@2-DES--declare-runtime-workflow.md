---
atom_family: SPEC
atom_id: AN-S-2603
container:
  component: C9
tier: 3
context:
  lens: DES
state:
  status: "archived"
  version: 2
  updated_at: "2026-11-25T23:01:36.890949+00:00"
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
