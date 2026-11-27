---
atom_family: TKT
atom_id: AN-T-3992
container:
  atom: AN-T-3476
priority: 2
context:
  template: task
  label: Task
state:
  status: "done"
  version: 1
  updated_at: "2026-11-27T03:08:37.495462+00:00"
---
## Summary

Verify Component tests against the Manifest and Solution

## Acceptance

Use exact Manifest and Solution revisions. Derive test obligations from declared inputs, outputs, failures, and effects, plus Solution paths that need witnesses.

Map existing tests to the behavior they assert. Report missing coverage, incorrect assertions, and tests that can pass when the declared behavior is violated.

Pilot on C30 carrier framing. Generate executable cases where the formal declarations determine the input and expected result. Reuse the existing test runner. Execute the Component to observe actual behavior.

Include a negative control that changes a required result or behavior. Report obligations as unresolved when the declarations cannot supply a checkable expectation.
