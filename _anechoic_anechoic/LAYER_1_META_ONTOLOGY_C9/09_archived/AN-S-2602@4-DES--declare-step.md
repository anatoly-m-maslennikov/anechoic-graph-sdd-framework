---
atom_family: SPEC
atom_id: AN-S-2602
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

Declare Step

## Claim

### Formal Claim

```CFEL
# model
Atom/(.Header.Role: Operations)/Step;

# instances
Step//$step;

$step{::1}((IS_CONTAINED_BY)) Workflow//$workflow;

IF $step {=0}((RUNS)) THEN $step {::1+}((CONTAINS)) Substep//$substep;

IF $step {>0}((RUNS)) THEN $step {::0}((CONTAINS));

IF $step {=0}((CONTAINS)) THEN $step {::1}((RUNS)) (in (Action, Workflow))//$selected
```

## Semantics

A Step is a unit of work within a Workflow.
