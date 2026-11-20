---
identity:
  atom_id: AN-S-2955
context:
  container:
    component: C9
  tier: 3
  lens: DES
state:
  status: draft
  version: 1
  updated_at: 2026-11-05 19:15:20 +0400
---
## Summary

Declare Construct Declaration as a Requirement Form

## Claim

### Prose Claim

This Form uses the Declaration contract.

### Formal Claim

```python
# model
allowed_values(address="Atom/(.Header.Context.Role in (Requirement)).Header.Context.Form", values=('Construct Declaration',))
subject_path(address="Atom/(.Header.Context.Role in (Requirement))/(.Header.Context.Form in (Construct Declaration))")
```

## Semantics

A Construct Declaration defines the structure and binding scope of a multi-expression language construct.
