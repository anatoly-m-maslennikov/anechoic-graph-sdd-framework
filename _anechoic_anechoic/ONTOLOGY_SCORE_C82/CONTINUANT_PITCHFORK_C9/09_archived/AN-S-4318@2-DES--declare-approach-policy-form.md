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
  version: 2
  updated_at: 2026-11-07 15:18:44 +0400
---

## Summary

Declare Approach Policy Form

## Claim

### Formal Claim

```CFEL
# model
Atom/(.Header.Form := Approach Policy);

# instances
Atom/(.Header.Form := Approach Policy)//$approach_policy.Header.Role:: [in (Requirement, Method, Evaluation, Delivery, Operations)]{::1}
```

## Semantics

An Approach Policy is conditional on its stated case. At every descendant where that case applies, a local Atom must bind the Policy to the actual case through SPECIALIZES. A reference alone is insufficient; the binding preserves parent constraints.
