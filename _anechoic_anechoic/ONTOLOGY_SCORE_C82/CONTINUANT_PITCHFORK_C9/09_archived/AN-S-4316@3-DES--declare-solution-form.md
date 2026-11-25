---
atom_family: SPEC
atom_id: AN-S-4316
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

Declare Solution Form

## Claim

### Formal Claim

```CFEL
# model
Atom.Header.Context.Form :: Solution;

# instances
FOR EACH $a[<Atom>, (.Header.Context.Form = Solution)]:
(
    $a.Header.Context.Role:: [in (Requirement, Method, Evaluation, Delivery, Operations)]{::1}
)
```

## Semantics

A Solution specifies the contribution that realizes a Scope Unit’s responsibility across the unit and its descendants. Its Role identifies the contribution.
