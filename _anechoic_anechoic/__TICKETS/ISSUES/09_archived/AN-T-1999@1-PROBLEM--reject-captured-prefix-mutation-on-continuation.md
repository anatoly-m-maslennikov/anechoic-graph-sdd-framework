---
atom_family: TKT
atom_id: AN-T-1999
container:
  component: C16
priority: 2
context:
  template: problem
state:
  status: archived
  version: 1
  updated_at: 2026-10-05 01:20:00 +0400
---
## Summary

Reject captured-prefix mutation on continuation

# Summary

Reject captured-prefix mutation on continuation

## Disposition

Resolved in the Journal source contract: continuation revalidates source and
captured-member hashes, rejects changed/deleted/unreadable/truncated captured
data, and permits bytes appended after the sealed prefix.
