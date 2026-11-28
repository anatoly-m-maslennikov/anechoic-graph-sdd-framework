---
atom_family: TKT
atom_id: AN-T-4093
container:
  atom: AN-T-4087
priority: 2
context:
  template: task
  label: Task
state:
  status: in_queue
  version: 1
  updated_at: '2026-11-28T08:08:02+00:00'
---
## Summary

Prepare v0.5.0 release notes and review the PR

## Work

Use C64 Public Release with exact main and candidate commits. Collect
completed Task and Epic evidence. Review the Git diff for changes that
the Tickets missed. Keep Version History brief and put the details in
the PR description. Include the Tools HTTP migration from /tools to /.

## Acceptance

Record the pinned base and head and the reviewed PR and Version History
drafts. Verify user-facing claims against the candidate receipts.
Check the final head. Recheck any gates whose inputs changed.

Reconcile publication evidence with AN-T-2043 and the current
Operator-owned Public Release boundary.

## Comparison base

GitHub `main` is `cfc8f2bb9e56601163f8bf9dcc8212ea74235eae`, with
Framework Version 0.4.4. Its tree matches the comparison merge base.
Refresh the remote pin when reviewing the final head.

C64 rendered private PR and Version History drafts for qualification
head `ce8841c1a4b30ca61484049229e1f53444e7b210`. The review uses the
pinned Git comparison and completed Ticket evidence. The notes cover
the Tools route change, native Setup path, and publication boundary.
Check the claims again against the final candidate and its receipts.

C64 refreshed both drafts for `cd3c911537d0213b33172713a2b66cdac4d68cf4`.
The public main pin is unchanged. The local protected-merge replay
produces the exact sealed tree. Verify the shipped behavior against
the image and installation receipts before publication.
