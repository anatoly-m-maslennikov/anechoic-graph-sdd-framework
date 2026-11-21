---
atom_family: SPEC
atom_id: AN-S-3260
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

Declare Step Run

## Claim

### Formal Claim

```CFEL
# model
Step Run ((NARROWER_THAN)) Execution;

# instances
Step Run//$run {::1}((IS_EXECUTION_OF)) Step//$definition
```

## Semantics

A Step Run is an actual execution of one Step within a Workflow Run.
