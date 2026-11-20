---
atom_family: SPEC
atom_id: AN-S-2152
structure:
  container:
    component: C00
  tier: 3
context:
  lens: DES
state:
  status: draft
  version: 1
  updated_at: 2026-11-04 16:07:35 +0400
---

## Summary

Declare Execution

## Claim

### Formal Claim

```CFEL
# model
Execution ((NARROWER_THAN)) Occurrent;

# instances
Execution//$execution {::1+}((IS_EXECUTED_BY)) Runtime//$runtime;

Execution//$producer {::0+}((PRODUCES)) Event//$event
```

## Semantics

An Execution is the actual performance of work.
