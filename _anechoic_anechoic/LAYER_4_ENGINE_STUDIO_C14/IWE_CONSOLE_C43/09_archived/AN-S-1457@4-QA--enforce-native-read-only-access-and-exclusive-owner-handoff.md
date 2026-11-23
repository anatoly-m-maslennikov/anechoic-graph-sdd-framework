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
  version: 4
  updated_at: 2026-11-04 07:39:08 +0400
---
## Summary

Enforce native read-only access and exclusive owner handoff

## Claim scope

The public-SQL guard for the in-memory DuckDB Projection.

## Claim

### Prose Claim

Trusted public SQL uses native single-query admission and native read-only transactions, executes the exact SQL once, returns complete results or explicit errors, and shares serialized access with indexing. It creates no file or network access, application retry, rollback, or recovery layer. DuckPGQ internal management functions are unsupported; their connection-invalidating failures are an explicit MVP limitation, not a promised function-capability sandbox.

## Details

| Fixture | Expected outcome |
| --- | --- |
| SELECT, CTE, and native GRAPH_TABLE query | Each executes once and returns the requested result without changing projected source rows. |
| Multiple statements or INSERT/UPDATE/DELETE/DDL/SET/COPY/ATTACH request | Rejected as unsupported or by the native read-only boundary; no source file changes. |
| File/network read or external-access enable attempt | It fails; external access remains disabled. |
| Ordinary invalid SQL followed by a valid query | The first returns its query error, the next returns valid rows; no query is retried. |
| Unsupported DuckPGQ management function that invalidates the connection | Explicit engine/unavailable error reaches the caller and stderr; the source files stay unchanged and no automatic recovery occurs. |
| Memory-heavy query under a bounded native test memory limit | Completes in memory or returns its memory error; no database, temporary-spill, or intermediate file is created. |
| Query completion followed by source refresh | Owner access is released; queries see the successful refreshed state. |
