---
atom_family: SPEC
atom_id: AN-S-4318
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

Declare Approach Policy Form

## Claim

### Formal Claim

```CFEL
# model
Atom.Header.Context.Form :: Approach Policy;

# instances
FOR EACH $a[<Atom>, (.Header.Context.Form = Approach Policy)]:
(
    $a.Header.Context.Role:: [in (Requirement, Method, Evaluation, Delivery, Operations)]{::1}
)
```

## Semantics

An Approach Policy is conditional on its stated case. At every descendant where that case applies, a local Atom must bind the Policy to the actual case through SPECIALIZES. A reference alone is insufficient; the binding preserves parent constraints.
