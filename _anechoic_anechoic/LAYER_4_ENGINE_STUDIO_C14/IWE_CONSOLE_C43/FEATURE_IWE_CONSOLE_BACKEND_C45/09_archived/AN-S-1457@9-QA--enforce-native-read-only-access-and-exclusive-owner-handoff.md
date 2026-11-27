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
  version: 9
  updated_at: 2026-11-10 20:47:54 +0400
---
## Summary

Enforce native read-only access and exclusive owner handoff

## Claim scope

The public-SQL guard for the file-backed DuckDB Projection.

## Claim

### Prose Claim

Trusted public SQL uses native single-query admission and trusted internal materialization, executes exact SQL once, returns complete bounded results or explicit errors, and shares serialized access with indexing. Public SQL cannot edit sources or projected source rows; owned database/spill writes are permitted. External file/network access, retry, rollback and recovery are unsupported. DuckPGQ management functions may invalidate the connection; that is an explicit MVP limitation, not a promised function sandbox.

## Details

Exercise native SELECT/CTE/GRAPH_TABLE success, multi-statement and DDL/DML/SET/COPY/ATTACH rejection, external-access failure, invalid-SQL recovery, connection-invalidating management failure, bounded-memory spill/resource error, and completion followed by source refresh. Each case preserves source bytes; owner release makes successful refreshed state visible.
