---
atom_family: SPEC
atom_id: AN-S-2365
container:
  component: C16
tier: 3
context:
  lens: DES
state:
  status: active
  version: 8
  updated_at: 2026-10-27 20:00:04 +0400
---
## Summary

Use shared selected-Run journaling only for actual query invocation

## Scope

Query Run evidence.

## Claim

### Prose Claim

FIND_AND_FETCH_JOURNAL_EVENTS **must** use the shared RunJournal contract for actual invocation and must not create a competing log, fake Run, or preview Event.

## Details

CA-D-527, CA-D-528, and CA-D-529 govern preview/execute distinction, durable evidence, and delivery placement; this route contributes no second executor or Journal format.
