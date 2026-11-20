---
atom_family: SPEC
atom_id: AN-S-2368
structure:
  container:
    component: C16
  tier: 3
context:
  lens: DES
state:
  status: active
  version: 8
  updated_at: 2026-10-27 20:00:05 +0400
---
## Summary

Return observable query result and limit evidence

## Scope

The query result envelope.

## Claim

### Prose Claim

FIND_AND_FETCH_JOURNAL_EVENTS **must** return the snapshot token, result selection, pagination state, coverage state, and recoverable diagnostics sufficient to distinguish complete, partial, invalid, and blocked outcomes.

## Details

The envelope reports evidence and limits without exposing credentials, secrets, or unselected Event content.
