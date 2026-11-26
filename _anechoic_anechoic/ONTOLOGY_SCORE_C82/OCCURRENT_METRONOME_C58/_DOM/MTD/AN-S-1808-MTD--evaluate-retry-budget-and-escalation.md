---
atom_family: SPEC
atom_id: AN-S-1808
container:
  component: C58
tier: 6
context:
  lens: DOM/MTD
state:
  status: active
  version: 36
  updated_at: '2026-11-25T21:00:38.977326+00:00'
---
## Summary

Evaluate retry budget **and** escalation

## Claim

### Prose Claim

These cases describe the legacy Plan and Hub retry configuration. A native Atom Header follows AN-S-3160.


the retry-policy Evaluation.


the retry-policy Evaluation **must** return `fail` **if** **any** of the following occurs:

- the initial failed Evaluation consumes a retry.
- an automatic retry exceeds the effective Implementation Retry Limit resolved under AN-S-2333 **and** enforced by CA-O-024-PROJECT_CONFIGURATION-ACTION--control-implementation-retries.
- starting a permitted fix-and-evaluate round is **not** counted once, **or** checking its permission again consumes another retry.
- a changed failure set **or** automatic next loop silently resets the budget.
- the last permitted retry fails **without** pausing **and** reporting remaining failures **to** the Operator.
- retrying bypasses a confidence gate, governing-Atom approval rule, **or** additional Operator constraint.
- successful completion under CA-O-016-PROJECT_CONFIGURATION-WORKFLOW--implement-evaluations-before-required-behavior still triggers another automatic repair retry.

earlier escalation required by governing authority **must not** be rejected merely because retries remain.
