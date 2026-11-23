---
atom_family: SPEC
atom_id: AN-S-2463
container:
  component: C16
tier: 4
context:
  lens: QA
state:
  status: archived
  version: 11
  updated_at: 2026-10-27 06:04:45 +0400
---
## Summary

Verify query snapshot excludes its own execution Events

# Summary

Verify query snapshot excludes its own execution Events

## Claim

The Tool's result frontier remains unchanged when shared Run evidence appends during its actual invocation.

## Test case

Capture the Journal byte-prefix before workflow/action-start recording, start an
admitted execute invocation that records actual Run evidence, and append an
unrelated later Event before result pagination.

## Acceptance criteria

Returned IDs and continuation remain exactly the pre-dispatch snapshot; own and
later Events are absent, the result exposes the initial token and prefix hash,
and a standalone Action performs the same capture before its Run evidence.

## Failure disposition

Reject self-inclusion, frontier growth, or an unreported source change.
