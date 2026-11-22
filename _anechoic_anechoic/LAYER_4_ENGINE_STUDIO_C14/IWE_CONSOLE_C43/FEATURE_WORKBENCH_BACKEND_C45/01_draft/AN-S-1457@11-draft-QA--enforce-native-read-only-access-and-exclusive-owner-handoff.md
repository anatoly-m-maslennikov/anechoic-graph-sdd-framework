---
atom_family: SPEC
atom_id: AN-S-1457
container:
  component: C45
tier: 5
context:
  lens: QA
state:
  status: draft
  version: 11
  updated_at: '2026-11-13T22:31:23.061386+00:00'
---
## Summary

Enforce native read-only access and exclusive owner handoff

## Claim scope

The public-SQL guard for the file-backed DuckDB Projection.

## Claim

### Prose Claim

Verify that trusted public SQL uses native single-query admission and trusted internal materialization.

## Details

- It executes the exact SQL once, returns complete bounded results or explicit errors,
  and shares serialized access with indexing.
- Public SQL cannot edit sources or projected source rows.
- Owned database and spill writes are permitted.

### MVP limitations

The MVP provides no function sandbox.

- External file and network access, retry, rollback, and recovery are unsupported.
- DuckPGQ management functions may invalidate the connection.

### Test cases

Verify that each case preserves source bytes:

- Native `SELECT`, CTE, and `GRAPH_TABLE` queries succeed.
- Multi-statement SQL, DDL, DML, `SET`, `COPY`, and `ATTACH` are rejected.
- External access fails. The connection remains usable after invalid SQL.
- A DuckPGQ management function can invalidate the connection.
- Under a memory limit, DuckDB spills to disk or returns a resource error.
- After the query completes, indexing refreshes the data.
  Owner release makes the refreshed state visible.
