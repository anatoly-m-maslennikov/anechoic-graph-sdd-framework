---
atom_family: SPEC
atom_id: AN-S-2604
container:
  component: C9
tier: 3
context:
  lens: DES
state:
  status: draft
  version: 2
  updated_at: 2026-11-11 14:06:22 +0400
---

## Summary

Declare Project Workflow

## Claim

### Formal Claim

```python
# model
allowed_values(address='Atom/(.Header.Context.Role in (Operations))/Workflow.Purpose', values=('Project',))
subject_path(address='Atom/(.Header.Context.Role in (Operations))/Workflow/(.Purpose in (Project))')
```

## Semantics

A Project Workflow develops, validates, maintains or releases a Project’s result.
