---
atom_family: SPEC
atom_id: AN-S-2243
structure:
  container:
    component: C43
  tier: 3
context:
  lens: DES
state:
  status: active
  version: 1
  updated_at: '2026-11-13T10:44:52.059934+00:00'
---
## Summary

Expose Project runtime data through DuckDB tables

## Claim scope

Read-only SQL over queryable runtime data for the selected Project.

## Claim

### Prose Claim

Expose queryable Project runtime data through DuckDB tables, `query_run` and `query_schema`. Include Atom and Scope Unit facts, direct and derived Relations, Archive allocation metadata, live Lifecycle Run list fields, query history, and published diagnostics. Reuse the same tables for runtime lookups where they serve the same data.

Apply the existing Project binding, retention and read-only rules. Keep pending Run input and private execution state out of SQL. Archive bodies load on demand.
