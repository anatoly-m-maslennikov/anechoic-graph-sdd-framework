---
atom_family: SPEC
atom_id: AN-S-4319
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

Declare Decision Form

## Claim

### Formal Claim

```CFEL
# model
Atom.Header.Context.Form :: Decision;

# instances
FOR EACH $a[<Atom>, (.Header.Context.Form = Decision)]:
(
    $a.Header.Context.Role:: [in (Method, Evaluation, Delivery, Operations)]{::1}
)
```

## Semantics

A Decision records a particular local choice. Applicable governing constraints continue to apply.
