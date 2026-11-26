---
atom_family: SPEC
atom_id: AN-S-4230
container:
  component: C9
tier: 3
context:
  lens: DES
state:
  status: archived
  version: 4
  updated_at: 2026-11-02 17:54:42 +0400
---

## Summary

Declare Substep

## Claim

### Formal Claim

```CFEL
# model
Atom/(.Header.Role: Operations)/Substep;

# instances
Substep//$substep{::1}((IS_CONTAINED_BY)) Step//$step;

Substep//$substep_2{::1}((RUNS)) Action//$action
```

## Semantics

A Substep is a leaf unit within a Step and runs exactly one reusable Action.
