---
atom_family: TKT
atom_id: AN-T-4031
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

Freeze benchmark checkouts and task corpus

## Work

Pin the current and pre-refactor revisions in disposable checkouts.
Select 15 small maintenance tasks across several Components before
running any trials. Use one prompt per task for both revisions. Describe
the expected behavior without naming the files to edit.

Use the same rule to select each source bundle. Include the relevant
Component and its dependency entry files. Apply the same context budget
to both revisions and record the bundle contents and size. Prepare
hidden acceptance tests that check the same behavior on both revisions.

## Acceptance

Record both revision IDs, bundle manifests, the 15 prompts, and the
acceptance tests. Verify that each task is applicable to both revisions
and that each baseline passes the relevant regression tests.
