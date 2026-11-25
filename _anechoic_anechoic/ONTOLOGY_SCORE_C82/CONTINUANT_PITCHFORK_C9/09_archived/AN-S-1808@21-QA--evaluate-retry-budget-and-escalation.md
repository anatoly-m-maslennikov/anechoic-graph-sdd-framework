---
atom_family: SPEC
atom_id: AN-S-1808
container:
  component: C9
tier: 6
context:
  lens: QA
state:
  status: archived
  version: 21
  updated_at: 2026-10-24 02:14:24 +0400
---
## Summary

Evaluate retry budget **and** escalation

# Summary

Evaluate retry budget **and** escalation

## Scope

the retry-policy Evaluation.

## Claim

the retry-policy Evaluation **must** return `fail` **if** **any** of the following occurs:

- the initial failed Evaluation consumes a retry.
- an automatic retry exceeds the effective Implementation Retry Limit resolved under CA-M-295-CORE_META_MODEL--resolve-implementation-retry-limits-by-source-precedence **and** enforced by CA-O-024-CORE_META_MODEL-ACTION--control-implementation-retries.
- starting a permitted fix-and-evaluate round is **not** counted once, **or** checking its permission again consumes another retry.
- a changed failure set **or** automatic next loop silently resets the budget.
- the last permitted retry fails **without** pausing **and** reporting remaining failures **to** the Operator.
- retrying bypasses a confidence gate, governing-Atom approval rule, **or** additional Operator constraint.
- successful completion under CA-O-016-CORE_META_MODEL-WORKFLOW--implement-evaluations-before-required-behavior still triggers another automatic repair retry.

earlier escalation required by governing authority **must not** be rejected merely because retries remain.

## Details
