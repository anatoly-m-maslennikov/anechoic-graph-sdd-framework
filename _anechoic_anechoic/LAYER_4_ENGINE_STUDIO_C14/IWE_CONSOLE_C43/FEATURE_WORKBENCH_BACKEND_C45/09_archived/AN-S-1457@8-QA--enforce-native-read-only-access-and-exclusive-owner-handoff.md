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
  version: 8
  updated_at: 2026-11-10 00:46:37 +0400
---

## Summary

Enforce native read-only access and exclusive owner handoff

## Claim scope

The public-SQL guard for the file-backed DuckDB Projection.

## Claim

### Prose Claim

Trusted public SQL uses native single-query admission and trusted internal materialization transactions, executes the exact SQL once, returns complete results through bounded pages or explicit errors, and shares serialized access with indexing. Public SQL cannot edit sources or projected source rows. Owned database and spill writes are permitted; external file/network access, application retry, rollback and recovery remain unsupported. DuckPGQ internal management functions are unsupported; their connection-invalidating failures are an explicit MVP limitation, not a promised function-capability sandbox.

## Details

| Fixture | Expected outcome |
| --- | --- |
| SELECT, CTE, and native GRAPH_TABLE query | Each executes once and returns its requested result through a file descriptor or explicitly requested inline page, without changing projected source rows. |
| Multiple statements or INSERT/UPDATE/DELETE/DDL/SET/COPY/ATTACH request | Rejected by native single-read-query admission; no source file changes. |
| File/network read or external-access enable attempt | It fails; external access remains disabled. |
| Ordinary invalid SQL followed by a valid query | The first returns its query error, the next returns a valid result; no query is retried. |
| Unsupported DuckPGQ management function that invalidates the connection | Explicit engine/unavailable error reaches the caller and stderr; the source files stay unchanged and no automatic recovery occurs. |
| Memory-heavy query under a bounded native test memory limit | Completes within the native memory budget using owned disk spill, or returns an explicit resource error. No source file is changed. |
| Query completion followed by source refresh | Owner access is released; queries see the successful refreshed state. |
