---
atom_family: SPEC
atom_id: AN-S-1399
container:
  component: C21
tier: 4
context:
  lens: QA
state:
  status: archived
  version: 5
  updated_at: 2026-09-17 02:10:33 +0000
---
## Summary

Reject transport that broadens one Tool boundary

# Reject transport that broadens one Tool boundary

## Claim checked

MCP cannot alter a canonical Tool's authority, cardinality, failure, **or** side-effect boundary.

## Test case

Forward one Atom Doer request while attempting **to** substitute a broader target set **or** success for a partial Tool outcome.

## Acceptance criteria

the request is rejected **or** the exact Tool outcome is retained; no broader **or** fabricated success crosses the boundary.

## Failure disposition

Stop the invocation **and** record the attempted semantic alteration.
