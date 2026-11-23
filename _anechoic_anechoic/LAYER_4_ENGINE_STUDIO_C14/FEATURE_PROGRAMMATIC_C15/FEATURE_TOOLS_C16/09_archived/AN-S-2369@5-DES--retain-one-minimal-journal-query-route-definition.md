---
atom_family: SPEC
atom_id: AN-S-2369
container:
  component: C16
tier: 3
context:
  lens: DES
state:
  status: archived
  version: 5
  updated_at: 2026-10-25 17:32:27 +0400
---
## Summary

Retain one minimal Journal query route definition

# Summary

Retain one minimal Journal query route definition

## Scope

The source-to-implementation route.

## Claim

FIND_AND_FETCH_JOURNAL_EVENTS **must** retain exactly one Workflow, one query Action, and one query Step as its source route.

## Details

Shared Run support remains shared infrastructure and does not become an additional Workflow or query Action.
