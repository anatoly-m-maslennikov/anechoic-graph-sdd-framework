---
identity:
  atom_id: AN-S-2463
context:
  container:
    component: C16
  tier: 4
  lens: QA
state:
  status: active
  version: 12
  updated_at: 2026-10-27 19:59:37 +0400
---
## Summary

Verify query snapshot excludes its own execution Events

## Claim

### Prose Claim

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
