---
atom_family: SPEC
atom_id: AN-S-2205
container:
  component: C9
tier: 3
context:
  lens: DES
state:
  status: archived
  version: 2
  updated_at: 2026-11-07 15:18:44 +0400
---

## Summary

Declare Requirement Form

## Claim

### Formal Claim

```CFEL
# model
Atom/(.Header.Form := Requirement);

# instances
Atom/(.Header.Form := Requirement)//$requirement.Header.Role:: [in (Requirement)]{::1}
```

## Semantics

A Requirement Form states a local required outcome, behavior, property or constraint.
