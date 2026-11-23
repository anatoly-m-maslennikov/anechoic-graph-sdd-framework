---
atom_family: SPEC
atom_id: AN-S-4719
container:
  component: C16
tier: 3
context:
  lens: DES
state:
  status: archived
  version: 5
  updated_at: 2026-10-24 13:39:34 +0400
---
## Summary

Wait for execution updates

# Summary

Wait for execution updates

## Scope

the WATCH_EXECUTION capability for Tool/WATCH_EXECUTION.

## Claim

the WATCH_EXECUTION Tool **must** return correlated execution updates after a caller's cursor, including completion, failure, interruption, handoff, progress, and evidence-recording changes.

## Details

- implement the methodology Action CA-O-117-PROJECT_CONFIGURATION-ACTION--watch-execution.
- accept a supported Run ID, opaque cursor and bounded wait timeout; return a new cursor, updates, current status, timeout state, and full report reference.
- preserve the Operator's choice of what **to** execute; discovery, context retrieval, **and** observation provide capabilities.
- bounded **or** unavailable evidence **must** remain explicit **rather than** establish a successful assessment.
