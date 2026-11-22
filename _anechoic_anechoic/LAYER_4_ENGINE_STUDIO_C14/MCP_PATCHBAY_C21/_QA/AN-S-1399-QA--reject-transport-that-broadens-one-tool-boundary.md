---
atom_family: SPEC
atom_id: AN-S-1399
container:
  component: C21
tier: 3
context:
  lens: QA
state:
  status: active
  version: 20
  updated_at: 2026-11-10 20:47:54 +0400
---

## Summary

Reject transport that broadens one Tool boundary

## Claim

### Prose Claim

MCP cannot alter a canonical Tool's authority, cardinality, failure, **or** side-effect boundary.

## Details

### Test case

Forward one Atom Doer request while attempting **to** substitute a broader target set **or** success for a partial Tool outcome.

### Acceptance criteria

the request is rejected **or** the exact Tool outcome is retained; no broader **or** fabricated success crosses the boundary.

### Failure disposition

Stop the invocation **and** record the attempted semantic alteration.
