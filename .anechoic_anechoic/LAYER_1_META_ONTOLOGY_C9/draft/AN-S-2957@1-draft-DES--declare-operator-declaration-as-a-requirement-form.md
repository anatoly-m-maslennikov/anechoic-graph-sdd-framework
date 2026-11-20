---
identity:
  atom_id: AN-S-2957
context:
  container:
    component: C9
  tier: 3
  lens: DES
state:
  status: draft
  version: 1
  updated_at: 2026-11-10 22:09:03 +0400
---
## Summary

Declare Operator Declaration as a Requirement Form

## Claim

### Prose Claim

This Form uses the Declaration contract.

### Formal Claim

```python
# model
allowed_values(address="Atom/(.Header.Context.Role in (Requirement)).Header.Context.Form", values=('Operator Declaration',))
subject_path(address="Atom/(.Header.Context.Role in (Requirement))/(.Header.Context.Form in (Operator Declaration))")
```

## Semantics

An Operator Declaration defines notation syntax and its operand rules.
