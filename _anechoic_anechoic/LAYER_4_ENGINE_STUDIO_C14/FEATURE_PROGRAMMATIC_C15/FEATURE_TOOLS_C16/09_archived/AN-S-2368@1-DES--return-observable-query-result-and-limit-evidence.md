---
atom_family: SPEC
atom_id: AN-S-2368
container:
  component: C16
tier: 3
context:
  lens: DES
state:
  status: archived
  version: 1
  updated_at: 2026-10-05 00:30:00 +0400
---
## Summary

Return observable query result and limit evidence

# Summary

Return observable query result and limit evidence

## Scope

The query result envelope.

## Claim

FIND_AND_FETCH_JOURNAL_EVENTS **must** return the snapshot token, result selection, pagination state, coverage state, and recoverable diagnostics sufficient to distinguish complete, partial, invalid, and blocked outcomes.

## Details

The envelope reports evidence and limits without exposing credentials, secrets, or unselected Event content.
