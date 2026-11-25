---
atom_family: SPEC
atom_id: AN-S-2599
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

Declare Workflow

## Claim

### Formal Claim

```CFEL
# model
Atom/(.Header.Role: Operations)/Workflow;

# instances
Workflow//$workflow{:1+}((CONTAINS)) Step//$step;

Workflow//$workflow_2{:0+}((IS_RUN_BY)) Step//$step_2
```

## Semantics

A Workflow defines a graph of Steps for governed work.
