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
  version: 3
  updated_at: 2026-11-11 14:06:22 +0400
---

## Summary

Declare Requirement Form

## Claim

### Formal Claim

```CFEL
# model
Atom.Header.Context.Form :: Requirement;

# instances
FOR EACH $a[<Atom>, (.Header.Context.Form = Requirement)]:
(
    $a.Header.Context.Role:: [in (Requirement)]{::1}
)
```

## Semantics

A Requirement Form states a local required outcome, behavior, property or constraint.
