---
identity:
  atom_id: AN-S-2161
context:
  container:
    component: C00
  tier: 3
  lens: DES
state:
  status: draft
  version: 1
  updated_at: 2026-11-04 16:07:35 +0400
---

## Summary

Declare Action Run

## Claim

### Formal Claim

```CFEL
# model
Action Run ((NARROWER_THAN)) Execution;

# instances
Action Run//$run {::1}((IS_EXECUTION_OF)) Action//$definition
```

## Semantics

An Action Run is an actual execution of one Action.
