---
atom_family: SPEC
atom_id: AN-S-1426
container:
  component: C37
tier: 4
context:
  lens: QA
state:
  status: archived
  version: 22
  updated_at: 2026-11-10 20:47:54 +0400
---
## Summary

Persist one Projection without mutating authority

# Persist one Projection without mutating authority

## Test case

Run description **and** ordinary generation **without** a destination; persist **to** one explicit valid Projection destination; repeat through one registered destination; **then** attempt an ambiguous destination, path traversal, symlink escape, **and** destinations inside Atom **and** Journal authority. Optionally let `GRAPH_UI` present the valid result.

## Acceptance criteria

**only** the explicit **or** unambiguous registered persistence replaces exactly one Projection Carrier atomically. Every authority **and** Journal byte remains unchanged. Invalid destinations fail **without** partial output. Optional `GRAPH_UI` presentation preserves the Projection’s source lineage **and** non-authoritative status; it cannot use the Projection as authority **or** mutate it.
