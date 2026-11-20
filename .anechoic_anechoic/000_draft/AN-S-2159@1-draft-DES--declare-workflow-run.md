---
atom_family: SPEC
atom_id: AN-S-2159
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

Declare Workflow Run

## Claim

### Formal Claim

```CFEL
# model
Workflow Run ((NARROWER_THAN)) Execution;

# instances
Workflow Run//$run {::1}((IS_EXECUTION_OF)) Workflow//$definition
```

## Semantics

A Workflow Run is an actual execution of one Workflow with supplied inputs and parameters.
