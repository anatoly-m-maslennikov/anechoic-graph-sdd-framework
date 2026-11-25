---
atom_family: TKT
atom_id: AN-T-3920
container:
  atom: AN-T-3916
priority: 2
context:
  template: task
  label: Task
state:
  status: in_queue
  version: 1
  updated_at: '2026-11-24T18:01:27.878141+00:00'
---

## Summary

Resume Local Release across repeated fixes

## Work

Keep one run ID, target Project, and allocated version through each failure, fix, and explicit continuation. Accept the corrected exact source revision for split verification and installation until delivery starts. Reuse successful phases only while their inputs and required evidence still match.

## Acceptance

- Exercise at least two failure, fix, and continuation cycles in one run. Verify that a canary-only fix reruns the MCP canary on the same image, and that a runtime fix builds and verifies a new image.
- Continue split verification from a corrected exact revision, then install the verified image on the target Manifest port. Reject mismatched source, target, and image evidence. Once delivery starts, reconcile the recorded artifact.
- Retain failure evidence. Complete verified startup, prod tagging, and cleanup in order.
