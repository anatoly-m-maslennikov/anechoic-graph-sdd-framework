---
atom_family: SPEC
atom_id: AN-S-2956
container:
  component: C9
tier: 3
context:
  lens: DES
state:
  status: draft
  version: 1
  updated_at: 2026-11-05 19:15:20 +0400
---
## Summary

Declare Function Declaration as a Requirement Form

## Claim

### Prose Claim

This Form uses the Declaration contract.

### Formal Claim

```python
# model
allowed_values(address="Atom/(.Header.Context.Role in (Requirement)).Header.Context.Form", values=('Function Declaration',))
subject_path(address="Atom/(.Header.Context.Role in (Requirement))/(.Header.Context.Form in (Function Declaration))")
```

## Semantics

A Function Declaration defines a pure function signature, including its input and output Formats; a predicate returns Bool.
