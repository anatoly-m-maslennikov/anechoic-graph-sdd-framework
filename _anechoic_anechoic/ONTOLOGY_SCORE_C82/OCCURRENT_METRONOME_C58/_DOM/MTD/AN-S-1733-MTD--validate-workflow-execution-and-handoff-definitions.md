---
atom_family: SPEC
atom_id: AN-S-1733
container:
  component: C58
tier: 3
context:
  lens: DOM/MTD
state:
  status: active
  version: 24
  updated_at: '2026-11-25T21:38:51.854767+00:00'
---
## Summary

Validate Workflow execution and handoff definitions

## Claim

### Prose Claim


a Workflow's declared execution **and** handoff behavior.


the Evaluation **must** check whether a Workflow's declared execution **and** handoff behavior is well formed under AN-S-1614 **and** AN-S-1615, independently of current executor availability.

## Details

### Cases and expected results

- complete input declarations, resolvable references to Actions and called Workflows, admitted transitions, explicit terminal outcomes, **and** declared capability requirements: pass this definition check **without** requiring a running executor.
- a missing required input declaration, unresolved definition reference, missing continuation-selection rule, **or** absent applicable approval condition: reject the affected definition.
- a well-formed definition whose selected executor lacks a declared capability, worker, **or** current permission: the definition remains valid; execution admission is blocked under AN-S-1614. do **not** report unavailable execution as malformed authority.
- a missing invocation input **or** runtime resource is an execution-admission problem rather than a definition defect **when** its required binding is correctly declared.
- a terminal handoff declares the target Revision, complete continuation inputs, reason, check evidence, **and** performed-effect account: accept its declared continuation boundary.
- a handoff definition resumes predecessor Steps, claims successor success **before** execution, bypasses approval, resets retries, **or** admits an unbounded continuation cycle: reject.
- a cross-Workflow Step route offered as a Run handoff: reject; the two boundaries have different endpoints **and** responsibilities.

report the exact failing source **and** condition. definition validity **must not** be reported as permission, execution readiness, successful execution, **or** evidence that a Run occurred.
