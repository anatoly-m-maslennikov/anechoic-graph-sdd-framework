---
identity:
  atom_id: AN-T-2014
context:
  container:
    component: C9
  tier: 3
  template: question
state:
  status: resolved
  version: 3
  updated_at: 2026-11-02 17:54:42 +0400
---
## Summary

Resolve Step definition details after model-instance deferral

## Question

How does a Step select its work and bind parameters?

## Resolution

The Operator confirmed:

- A Step runs exactly one Action or Workflow, or contains one or more Substeps.
- RUNS and CONTAINS are mutually exclusive; a Step is nonempty.
- Step parameter bindings use previous Step outputs, enclosing Workflow Run input, or values fixed by the Step.
- The same sources apply to called Workflow inputs.

Detailed Workflow-instance review remains deferred.
