---
atom_family: SPEC
atom_id: AN-S-1457
container:
  component: C43
tier: 5
context:
  lens: QA
state:
  status: archived
  version: 2
  updated_at: 2026-11-04 00:38:14 +0400
---
## Summary

Enforce native read-only access and exclusive owner handoff

## Claim scope

The public-SQL guard for the in-memory DuckDB Projection.

## Claim

### Prose Claim

The selected native public-SQL guard for in-memory DuckDB rejects Projection-changing SQL, including data-modifying CTEs, and leaves in-memory rows unchanged. External access is disabled and locked before public SQL, so file and network reads fail. The query holds database access until it completes or fails, then releases it for the indexer. This handoff is between query and indexing work, without hot reload or owner replacement.

## Details

| Fixture | Expected outcome |
| --- | --- |
| Valid `SELECT` | It succeeds without changing a projected row. |
| `INSERT`, `UPDATE`, `DELETE`, or data-modifying CTE | The native guard rejects it; no state change is visible. |
| File/network read or configuration-enable attempt | It fails; external access remains disabled. |
| Failed query followed by valid query | The failure reaches its caller and does not corrupt the in-memory Projection. |

| Multi-statement SQL, DDL, DML, SET, COPY or ATTACH | Native statement classification rejects it before execution. |
| Memory-heavy public query under a bounded test memory limit | It either completes in memory or returns an explicit out-of-memory error; no temporary spill, database or intermediate file is created. |
| Query completion or failure followed by index refresh | Database access is released; the indexer applies its update atomically and later queries see the committed result. |
