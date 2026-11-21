---
atom_family: SPEC
atom_id: AN-S-3254
container:
  component: C00
tier: 3
context:
  lens: DES
state:
  status: archived
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
