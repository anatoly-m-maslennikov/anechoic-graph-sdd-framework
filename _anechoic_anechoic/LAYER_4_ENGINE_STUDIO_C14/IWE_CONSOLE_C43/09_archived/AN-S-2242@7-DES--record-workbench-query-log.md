---
atom_family: SPEC
atom_id: AN-S-2242
container:
  component: C43
tier: 3
context:
  lens: DES
state:
  status: archived
  version: 7
  updated_at: 2026-11-10 20:47:54 +0400
---

## Summary

Record Workbench Query Log

## Claim

### Prose Claim

Each actual query Run, whether successful or failed, **must** add one temporary query-log entry. A Check **must not** add a query-log entry. The entry **must** contain the original query SQL exactly, the success/fail outcome, the error when execution fails, the row count and the column count. A technical ID and timestamp are allowed.

The backend and MCP **must** expose the same query-log list and fetch capability. Query-log entries **must** expire after two days (48 hours) when the log is used; no cleanup daemon is required. The log **must not** store result rows, extra schema data or a deleted-result restoration mechanism. A preview **must** limit the returned rows without changing the SQL recorded in the log.

Bookmarks and saved Views remain separate from the temporary query log and do not expire with it.

Automatic query history may become visible after the Run response. A history-write failure must not discard or alter a completed Run or explicit Save result.
