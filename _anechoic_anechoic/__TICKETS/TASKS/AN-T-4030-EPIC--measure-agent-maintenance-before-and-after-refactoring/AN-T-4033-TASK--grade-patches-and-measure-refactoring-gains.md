---
atom_family: TKT
atom_id: AN-T-4033
container:
  atom: AN-T-4030
priority: 2
context:
  template: task
  label: Task
state:
  status: in_queue
  version: 1
  updated_at: "2026-11-26T21:41:33Z"
---
## Summary

Grade patches and measure refactoring gains

## Work

Grade the responses from AN-T-4032 outside the agent sessions. Apply
each patch as submitted to its pinned checkout. Run the same hidden
acceptance checks for each pair. Record patches that fail to apply,
fail tests, or pass.

## Acceptance

Report pass rate first. Report tokens and wall time per passing task,
including the effort spent on failed runs. Show input, cached input,
and output separately. For tasks that pass on both revisions, report
the median paired difference. Retain per-run evidence and describe the
result as the combined effect of the changes between the two revisions.
