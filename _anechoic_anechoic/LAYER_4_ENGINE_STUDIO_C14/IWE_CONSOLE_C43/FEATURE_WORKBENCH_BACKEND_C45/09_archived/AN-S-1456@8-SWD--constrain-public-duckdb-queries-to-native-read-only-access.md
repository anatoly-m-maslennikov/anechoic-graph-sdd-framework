---
atom_family: SPEC
atom_id: AN-S-1456
container:
  component: C45
tier: 4
context:
  lens: SWD
state:
  status: archived
  version: 8
  updated_at: 2026-11-05 13:04:02 +0400
---

## Summary

Constrain public DuckDB queries to native read-only access.

## Claim scope

Trusted public SQL and internal result materialization for one Project.

## Claim

Admit one read query from trusted Operator input through MCP or the Workbench web interface with DuckDB's native parsing and query APIs, including DuckPGQ's SQL/PGQ grammar. Use native tokenization where statement extraction does not support that grammar. Do not introduce a SQL parser, function sandbox or second query language.

Execute the accepted query once into a generated internal result table in the Project's derived DuckDB database. This trusted cache write uses a normal native transaction with COMMIT; public input remains SELECT-only and cannot submit DDL or DML. Read native ordered column metadata before materialization and retain it separately, including duplicate names. Deliver bounded pages from that stable result, not the entire result in a Python list. If query_run receives a non-negative preview, apply DuckDB's native relation.limit(N) to cap the result at most at N rows while preserving an existing SQL LIMIT; do not rewrite the submitted SQL or its text, and support GRAPH_TABLE and CTE queries. Counts and pagination describe that capped execution.

Run returns the exact selected SQL, including comments, Unicode and any existing LIMIT. When query_run requests save, append the saved query only after the successful materialization, using the exact selected SQL. A save failure does not discard the completed result: return its query ID and rows with outcome partial and save_error, without retry or rollback. A failed query never creates a saved entry. Run without save, Check and Page have no Journal effect.

Trusted startup loads the bundled DuckPGQ extension before disabling external access, extension autoinstall/autoload and public configuration changes. Permit database and spill writes only in the owned Workbench runtime directory. Source files remain unchanged.

Known invalid requests, unknown result IDs, rejected SQL, storage and result-delivery errors return their useful reason to the originating MCP or web caller and report stderr. They are not successful empty results or retried requests. An ordinary rejected query leaves a valid owner available. A failed owner reports Workbench-unavailable and restart-required; unexpected internal failures use the existing generic public error boundary.

DuckPGQ internal management calls remain unsupported and may invalidate the connection. This trusted-input MVP does not promise a capability sandbox. Do not add automatic query retries, rollback, retained-state restoration or connection recovery.

When preview is omitted, Run applies no added preview cap.
