---
atom_family: TKT
atom_id: AN-T-4049
container:
  atom: AN-T-3476
priority: 2
context:
  template: task
  label: Task
relations:
  IS_BLOCKED_BY:
  - AN-T-4048
state:
  status: "done"
  version: 1
  updated_at: "2026-11-27T02:09:29.113648+00:00"
---
## Summary

Review Spec Engine formal Specs against code

## Acceptance

Review the updated C75 Specs and their in-scope child Specs against the
pinned implementation. Check boundaries, observable outcomes, and
delegation. Use Lean comparisons where supported. Treat C50 and its Seeds
as an external dependency through the declared interface.

Record confirmed mismatches with Spec pins, source locations, and
reproducible evidence. Record unresolved comparisons and the evidence
needed to resolve them.

## Evidence

The review reproduced missing source context after verifier errors,
untyped snapshot Header failures, skipped validation in offline Structure
compilation, and incorrect interpretation of legacy delegation pins. It
also clarified that invalid framing generation raises an explicit error.

The repeat review reproduced Structure admission and checkpoint gaps,
missing sibling binding checks, and inconsistent mixed-profile entry
points. It confirmed those failures with disposable startup cases and
pinned Lean controls. See `an-t-3476-repeat-review.md`.
