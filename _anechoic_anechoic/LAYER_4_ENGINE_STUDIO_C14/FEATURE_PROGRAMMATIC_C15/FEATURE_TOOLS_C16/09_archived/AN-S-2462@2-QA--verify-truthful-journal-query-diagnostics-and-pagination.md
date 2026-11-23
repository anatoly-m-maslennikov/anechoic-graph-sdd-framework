---
atom_family: SPEC
atom_id: AN-S-2462
container:
  component: C16
tier: 3
context:
  lens: QA
state:
  status: archived
  version: 2
  updated_at: 2026-10-05 01:20:00 +0400
---
## Summary

Verify truthful Journal query diagnostics and pagination

# Summary

Verify truthful Journal query diagnostics and pagination

## Claim

The Tool reports malformed Events, missing IDs, duplicate fields, incomplete reads, source changes, coverage, and page limits without silently skipping them.

## Test case

Introduce fixtures for raw duplicate JSON object keys before parsing, duplicate
Event IDs across captured members, malformed/missing-ID/incomplete reads,
frontier-member/per-member-byte/total-read exhaustion, and a bounded multi-page
snapshot. Continue after changed, deleted, truncated, unreadable captured
members and after an append outside the sealed prefix.

## Acceptance criteria

Every rejection identifies its exact diagnostic and configured/consumed limit
evidence; changed, deleted, truncated, or unreadable captured members reject
continuation, while append after the sealed prefix preserves it. No affected
fixture is reported complete.

## Failure disposition

Reject silent omission, invented completeness, or pagination across an unbound frontier.
