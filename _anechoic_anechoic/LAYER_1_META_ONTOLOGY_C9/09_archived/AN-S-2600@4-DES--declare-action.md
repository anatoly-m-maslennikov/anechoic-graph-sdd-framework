---
atom_family: SPEC
atom_id: AN-S-2600
container:
  component: C9
tier: 3
context:
  lens: DES
state:
  status: archived
  version: 4
  updated_at: 2026-11-11 16:04:42 +0400
---

## Summary

Declare Action

## Claim

### Formal Claim

```CFEL
# model
Atom/(.Header.Context.Role in (Operations))/Action;

Action ((NARROWER_THAN)) Atom/(.Header.Context.Role in (Operations));

# instances
Action//$action{::0+}((IS_RUN_BY)) (in (Step, Substep))//$selected
```

## Semantics

An Action is a reusable operational building block. Its boundary reflects one modeled responsibility.
