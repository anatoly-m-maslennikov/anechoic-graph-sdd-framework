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
  version: 2
  updated_at: 2026-11-04 00:38:14 +0400
---

## Summary

Place the DuckDB Projection in rebuildable runtime state

## Claim scope

The in-memory placement and authority boundary of the Workbench query Projection.

## Claim

### Prose Claim

The existing application must own the rebuildable DuckDB Projection and Reader Schema Projection in memory. Source files are read directly; no DuckDB database file, derived database path, on-disk schema, cache, or stored intermediate source or materialized data is delivered. The public table surface remains the in-memory `atoms` and `scope_units` tables.

The source files remain the authority. The in-memory Projection is rebuildable and does not edit, move, archive, promote, or replace source Atoms. This Draft does not introduce a hot-swap owner or replacement-generation contract.

Any native read-only mechanism for an in-memory DuckDB connection remains an implementation research item. This Draft makes no promise about file-based read-only configuration.

