---
atom_family: SPEC
atom_id: AN-S-2363
container:
  component: C16
tier: 3
context:
  lens: DES
state:
  status: active
  version: 9
  updated_at: 2026-10-27 20:00:04 +0400
---
## Summary

Report complete query diagnostics and bounded coverage

## Scope

Query failure and coverage reporting.

## Claim

### Prose Claim

FIND_AND_FETCH_JOURNAL_EVENTS **must** reject and report malformed Events, raw
duplicate JSON keys before parse, missing IDs, duplicate IDs across the captured
frontier, incomplete reads, invalid filters, changed/deleted/truncated captured
members, configurable-budget exhaustion, coverage, and pagination truthfully
without silent skipping.

## Details

The shared configured maxima govern request bytes, expression depth, filter
tokens, IN members, page size, selected fields, frontier members, per-member
bytes, total read bytes, timeout, and retained findings. Each result identifies
the applicable configured limit and consumption/exhaustion state, scanned
coverage, matched and returned counts when determinable, continuation
availability, and every blocking or partial-read diagnostic.
