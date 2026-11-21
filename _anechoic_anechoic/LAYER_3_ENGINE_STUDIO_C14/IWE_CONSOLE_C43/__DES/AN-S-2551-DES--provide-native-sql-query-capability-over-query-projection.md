---
atom_family: SPEC
atom_id: AN-S-2551
structure:
  container:
    component: C43
  tier: 3
context:
  lens: DES
state:
  status: active
  version: 10
  updated_at: '2026-11-13T10:11:03.466775+00:00'
---
## Summary

Provide native SQL query capability over query projection

## Claim scope

Queries over the synchronized Atom query Projection.

## Claim

### Prose Claim

Keep SQL read-only for sources and Projection. Run and Check execute synchronously against the query Projection. Each request executes one complete query; cursor position is caret metadata only, and multiple statements are rejected. Native selected-engine semantics determine accepted SQL. Invalid SQL returns a query error distinct from a source-file failure, and execution changes neither sources nor the Projection.

Expose parsed Header/Content without flattening distinctions. Read-only `query_schema({})` returns actual `atoms` (including declared `content.*` and Mode-2 Header Status columns with optional distinct non-null values) and `scope_units`; fetching it neither runs SQL nor reads/writes saved Journal. Status completion can properly escape an actual value from that metadata.

Expose queryable Project runtime data as read-only DuckDB tables through `query_run` and `query_schema`. Reuse existing tables for lookups. Include Atom and Scope Unit facts, direct and derived Relations, Archive allocation metadata, live Lifecycle Run list fields, query history and published audit diagnostics. Use the existing Project binding and retention rules. Keep pending input and private execution state out of SQL.

Persistent saving, loading and saved-item listing are separate contracts; unsaved Run, Check and Page have no saved-item side effect.
