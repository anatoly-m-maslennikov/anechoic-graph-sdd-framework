---
identity:
  atom_id: AN-S-1456
context:
  container:
    component: C45
  tier: 4
  lens: SWD
state:
  status: draft
  version: 15
  updated_at: '2026-11-13T22:31:13.156861+00:00'
---
## Summary

Constrain public DuckDB queries to native read-only access.

## Claim scope

Trusted public SQL and internal result materialization for one Project.

## Claim

### Prose Claim

#### Admission

One whole trusted read query is admitted through MCP or the Workbench web interface using DuckDB native parsing and query APIs, including DuckPGQ SQL/PGQ. Run and Check do not select a statement or fragment at the cursor. Native tokenization applies when extraction cannot support the grammar. There is no added SQL parser, function sandbox or second query language.

#### Execution and pages

The accepted SELECT-only query executes once into a DuckDB-owned generated result table in a normal native transaction. Public input cannot submit DDL or DML. The trusted cache write may COMMIT. Ordered native column metadata, including duplicates, is retained. Bounded pages come from the stable result.

Preview uses native `relation.limit(N)` without rewriting submitted SQL. It preserves an existing SQL LIMIT, supports CTE and GRAPH_TABLE, and changes counts to the capped execution. Without preview there is no added cap.

Exact submitted SQL, including comments, Unicode and LIMIT, stays internal. Ordinary Run, Check and Page responses do not echo it. Save appends the Bookmark only after materialization. A save failure returns the completed result ID and metadata with `outcome: partial` and `save_error`, without retry or rollback. Failed queries create no saved entry. Unsaved Run, Check and Page have no Journal effect.

Page transforms use only the existing result table. They do not rerun, parse, append to or rewrite SQL. Materialization uses one native cache with a private quoted ordinal before public columns; preview applies before snapshot numbering. Public indices resolve to physical positions, not user names or DuckDB `rowid`. The ordinal is the final stable page tie-breaker; it is not public metadata or a filter or group value. Literal filter values are bound with native DuckDB. Ordering uses `NULLS LAST`, group order before sort, and window counts before offset and limit. There is no second cache, ALTER, UPDATE, rescan, raw SQL grid clause, endpoint or service.

#### Lifecycle and errors

The dedicated result lifecycle owns retention, View pinning, restart disposal and runtime-setting reads. Startup loads bundled DuckPGQ before disabling external access, autoinstall, autoload and public configuration changes. Database and spill writes stay in the owned runtime directory. Sources stay unchanged.

Reject, unknown, storage and delivery errors return useful caller reasons and stderr diagnostics. Invalid requests are recoverable `query_error` WARNING failures. Unavailable or unexpected owner failures are ERROR/blocked with the existing restart or generic boundary. DuckPGQ management calls may invalidate the connection. This trusted-input MVP promises no capability sandbox, retry, restoration or connection recovery.
