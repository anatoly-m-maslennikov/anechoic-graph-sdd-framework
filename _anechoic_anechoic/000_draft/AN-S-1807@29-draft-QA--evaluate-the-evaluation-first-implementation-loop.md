---
atom_family: SPEC
atom_id: AN-S-1807
structure:
  container:
    component: C00
  tier: 4
context:
  lens: QA
state:
  status: draft
  version: 29
  updated_at: 2026-11-02 18:35:20 +0400
---
## Summary
Evaluate the Evaluation-first implementation loop

## Claim

within the anechoic Project, the implementation-loop Evaluation **must** return `fail` **if**

- unchanged mode, RMED, **and** complete execution inputs yield different applicable tasks **or** ordering,
- a consumer runs **before** its prerequisite,
- Atom ID overrides a prerequisite,
- a cycle is admitted,
- feasible Evaluation-preparation precedence is omitted **or** left implicit,
- **or** an absolute E-first barrier prevents preparation of an Evaluation prerequisite.

it **must** also return `fail` **if**

- applicable Methods **or** Delivery boundaries are omitted from Evaluation **or** Requirement implementation,
- Atom ID resolves a Method conflict,
- preparation of an Evaluation is reported as its execution,
- **or** completion is reported with **any** applicable Evaluation failed, blocked, **or** unevaluated.

repeated evaluate-fix execution **and** runtime loops alone **must not** be rejected as prerequisite cycles.
