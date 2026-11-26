---
atom_family: SPEC
atom_id: AN-S-4647
container:
  component: C9
tier: 3
context:
  template: action
  lens: DevOps
state:
  status: archived
  version: 9
  updated_at: 2026-10-23 03:06:32 +0400
---
## Summary

Diagnose implementation test failures

# Summary

Diagnose implementation test failures

## Operation

Implementation Failure Diagnosis **means** the Agentic Action that explains failed implementation checks **before** choosing a recovery route.

- inputs: the selected P/Plan item, actual failure output, failing candidate, prepared tests, execution phase, current R/E/D **and** Method bindings, complete relevant inputs, **and** applicable confidence/permission gates.
- inspect the failing assertion, expected behavior, code path, test setup, **and** reproducibility. a failing test alone does **not** prove an implementation defect **or** a missing Method.
- return `expected_initial_failure` **only** **when** a correct prepared test exposes selected behavior **not** implemented yet; retain that test's initial failure evidence. this is normal test-first progress, **not** a failed repair retry **or** a reason **to** invent a corrective Method.
- return `implementation_defect` for incorrect production code **or** `test_implementation_defect` for incorrect executable test code, with evidence, affected work, **and** proposed correction. **every** admitted repair still passes through retry control.
- return `authority_change_required` for incorrect, missing, **or** conflicting governing expected behavior; return `environment_blocker` for unavailable execution prerequisites outside the admitted correction; return `unresolved` **when** evidence **or** confidence is insufficient.
- do **not** modify code, governing Atoms, Status, **or** test expectations. report failures honestly; do **not** relabel an unexplained failure as expected merely **to** proceed.

- accept actual confirmed code-review findings as diagnosis input as well as failed checks; inspect their evidence and classify under the same existing results. Do not fabricate test failures or classify unfinished review as a defect. Preliminary pending checks cannot be an accepted-candidate claim.

## Details
