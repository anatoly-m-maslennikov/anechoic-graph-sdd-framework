---
atom_family: SPEC
atom_id: AN-S-2363
concern:
  subject: "Event Record"
  path: "Model/Graph/Node//Artifact//SSOT//Recorded"
  relation: "is_narrower_than"
container:
  component: C16
tier: 3
context:
  lens: DES
state:
  status: active
  version: 10
  updated_at: "2026-11-27T16:16:01.404965+00:00"
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
