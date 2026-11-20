---
identity:
  atom_id: CA-M-462
  ref_id: CA-M-462@15-draft
context:
  container:
    scope_unit: CA-SU-45
  role: Method
  form: Decision
  topics:
    main_subject: PROJECT STRUCTURE//ANECHOIC <+ Aspects <+ Engineering <+ Operation
      <+ Data Handling <+ Query Processing
    dependencies:
    - MODEL//ANECHOIC <+ Projection
  tier: 4
relations:
  method_for:
  - CA-R-2728
  - CA-R-2953
  IS_REPLACEMENT_FOR:
  - CA-M-462
state:
  status: draft
  version: 15
  updated_at: '2026-11-13T22:31:13.156861+00:00'
destination:
  file:
    name: CA-M-462@15-draft-WORKBENCH_BACKEND-DECISION--constrain-public-duckdb-queries-to-native-read-only-access.md
    path: .anechoic_anechoic/CA-SU-14_LAYER_2_FRAMEWORK_ENGINE/CA-SU-15_FEATURE_PROGRAMMATIC/CA-SU-20_FEATURE_APPS/CA-SU-43_APP_WORKBENCH/CA-SU-45_FEATURE_WORKBENCH_BACKEND/05_method/000_draft
current_scope_unit: WORKBENCH_BACKEND
claim_target_scope_unit: WORKBENCH_BACKEND
author: Anatoly Maslennikov
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
