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
  version: 19
  updated_at: 2026-11-02 19:44:26 +0400
---
## Summary

Persist one Projection without mutating authority

# Persist one Projection without mutating authority

## Test case

Run description **and** ordinary generation **without** a destination; persist **to** one explicit valid Projection destination; repeat through one registered destination; **then** attempt an ambiguous destination, path traversal, symlink escape, **and** destinations inside Atom **and** Journal authority. Let `GRAPH_SERVER` read the valid result **and** optionally let `GRAPH_UI` present it.

## Acceptance criteria

**only** the explicit **or** unambiguous registered persistence replaces exactly one Projection Carrier atomically. Every authority **and** Journal byte remains unchanged. Invalid destinations fail **without** partial output. `GRAPH_SERVER` exposes the Projection read-only with its source lineage **and** non-authoritative status; optional `GRAPH_UI` presentation does not change that status; neither can use it as authority **or** mutate it.
