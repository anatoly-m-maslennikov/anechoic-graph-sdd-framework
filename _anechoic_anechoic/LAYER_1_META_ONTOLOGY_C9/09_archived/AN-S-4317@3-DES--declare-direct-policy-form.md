---
atom_family: SPEC
atom_id: AN-S-4317
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

Declare Direct Policy Form

## Claim

### Formal Claim

```CFEL
# model
Atom.Header.Context.Form :: Direct Policy;

# instances
FOR EACH $a[<Atom>, (.Header.Context.Form = Direct Policy)]:
(
    $a.Header.Context.Role:: [in (Requirement, Method, Evaluation, Delivery, Operations)]{::1}
)
```

## Semantics

A Direct Policy applies to all descendants recursively without a local copy. A genuine SPECIALIZES Atom may add applicable detail while preserving parent constraints.
