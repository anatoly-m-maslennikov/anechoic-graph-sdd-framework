---
atom_family: SPEC
atom_id: AN-S-4701
container:
  component: C9
tier: 3
context:
  template: step
  lens: DevOps
state:
  status: archived
  version: 7
  updated_at: 2026-10-24 01:18:03 +0400
---
## Summary

Perform the read-only semantic code review

# Summary

Perform the read-only semantic code review

## Operation

This Step invokes CA-O-225 in Isolated context only when that context is admitted. Bind candidate, owned paths, all actual Evaluation/diagnosis results, selected Plan or actual admitted in-session P/task with instruction/Definition of Done/source context, direct full `requirements`, `methods`, `evaluations`, and `delivery` rows, Project Principles, permissions, allowed commands, source revisions/hashes, report, and Run ID. An optional legacy `method_projection` may accompany direct rows but is not required.

Check evidence coverage and selected Method-policy compliance without restating policy. Map `implementation_defect` and `test_implementation_defect` to completed `findings`; map `authority_change_required`, `environment_blocker`, and `unresolved` to `unresolved` with actual results retained; report `expected_initial_failure` as an expected-phase observation and never accept the candidate unless admitted expected-phase criteria genuinely hold. Return `passed`, completed `findings`, `partial`, or `unresolved` according to CA-O-225.

## Details

No auto-fix, source/Atom edit, expected-result edit, retry, promotion, release, or Journal-completeness gate. Temporary fixture writes require explicit permission.
