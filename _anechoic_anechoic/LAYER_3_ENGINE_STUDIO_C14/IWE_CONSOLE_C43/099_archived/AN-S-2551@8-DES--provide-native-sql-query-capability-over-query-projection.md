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
  status: archived
  version: 8
  updated_at: 2026-11-10 20:47:54 +0400
---
## Summary

Provide native SQL query capability over query projection

## Claim scope

Queries over the synchronized Atom query Projection.

## Claim

### Prose Claim

Keep SQL read-only for sources and Projection. Run and Check execute synchronously against the query Projection. Each request executes one complete query; cursor position is caret metadata only, and multiple statements are rejected. Native selected-engine semantics determine accepted SQL. Invalid SQL returns a query error distinct from a source-file failure, and execution changes neither sources nor the Projection.

Expose parsed Header/Content without flattening distinctions. Read-only `query_schema({})` returns actual `atoms` (including declared `content.*` and Mode-2 Header Status columns with optional distinct non-null values) and `scope_units`; fetching it neither runs SQL nor reads/writes saved Journal. Status completion can properly escape an actual value from that metadata.

Persistent saving, loading and saved-item listing are separate contracts; unsaved Run, Check and Page have no saved-item side effect.
