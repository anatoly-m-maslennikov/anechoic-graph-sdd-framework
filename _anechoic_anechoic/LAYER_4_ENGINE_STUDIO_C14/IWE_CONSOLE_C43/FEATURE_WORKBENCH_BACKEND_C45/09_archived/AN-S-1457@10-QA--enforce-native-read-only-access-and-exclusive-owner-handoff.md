---
atom_family: SPEC
atom_id: AN-S-1457
container:
  component: C45
tier: 5
context:
  lens: QA
state:
  status: archived
  version: 10
  updated_at: '2026-11-13T20:53:53.520734+00:00'
---
## Summary

Enforce native read-only access and exclusive owner handoff

## Claim scope

The public-SQL guard for the file-backed DuckDB Projection.

## Claim

### Prose Claim

Verify that trusted public SQL uses native single-query admission and trusted internal materialization. It executes exact SQL once, returns complete bounded results or explicit errors, and shares serialized access with indexing. Public SQL cannot edit sources or projected source rows; owned database and spill writes are permitted. External file and network access, retry, rollback and recovery are unsupported. DuckPGQ management functions may invalidate the connection. This is an explicit MVP limitation, not a promised function sandbox.

## Details

Exercise native SELECT, CTE and GRAPH_TABLE success; rejection of multi-statement, DDL, DML, SET, COPY and ATTACH input; external-access failure; invalid-SQL recovery; connection-invalidating management failure; bounded-memory spill or resource error; and completion followed by source refresh. Each case preserves source bytes. Owner release makes successful refreshed state visible.
