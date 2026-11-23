---
atom_family: SPEC
atom_id: AN-S-1362
container:
  component: C43
tier: 4
context:
  lens: DevOps
state:
  status: archived
  version: 1
  updated_at: 2026-11-03 23:17:14 +0400
---

## Summary

Place the DuckDB Projection in rebuildable runtime state

## Claim scope

The delivery boundary and ownership of the per-Project DuckDB Projection state.

## Claim

### Prose Claim

Deliver the rebuildable query database inside the existing Project Docker/runtime boundary. Its concrete path is runtime state, not another governing source or configuration artifact.

The Projection instance identity follows the existing rule when first created and remains the same across rebuilds. Delivery does not allocate a pre-created identity or make the database authoritative. It does not edit, move, archive or promote source Atoms.

Use the existing Docker application's stdout/stderr boundary for technical output. Source-file errors go to stderr, not query-result records.
