---
identity:
  atom_id: AN-S-2151
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

Declare Runtime

## Claim

### Formal Claim

```CFEL
# model
Runtime ((NARROWER_THAN)) Occurrent;

# instances
Runtime//$runtime {::0+}((EXECUTES)) Execution//$execution
```

## Semantics

A Runtime is an environment in which Executions run.
