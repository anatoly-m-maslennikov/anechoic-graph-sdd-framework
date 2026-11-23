---
atom_family: SPEC
atom_id: AN-S-2566
container:
  component: C43
tier: 6
context:
  template: DECISION
  lens: DES/DOM
state:
  status: archived
  version: 1
  updated_at: 2026-11-03 23:17:14 +0400
---

## Summary

Execute one read-only DuckDB query

## Claim scope

One public native-SQL Run or Check request against one committed Project query Projection.

## Claim

Execute one read-only DuckDB query **means** the direct request-time Action that performs the exact SQL supplied by an originating MCP or web Run or Check request through the Project's shared query owner. Existing trusted caller information may remain internal to that request only when needed to deliver its response; it is not a new public argument or context contract.

## Details

1. Serialize the direct request with Projection reconciliation. Begin only after any trusted read-write synchronization handle is closed, then open the database in native read-only mode. Do not overlap read-only and read-write handles for the same database file. Do not create a query job, ticket, queue, planner, scheduler, orchestrator, or background query process.
2. Use native DuckDB SQL semantics, not a keyword filter or custom SQL parser. Before public SQL is accepted, use the owner's trusted setup with only required helpers registered, external access disabled, and that configuration locked. The read-only connection is the enforcement boundary for writes, including a data-modifying CTE.
3. Execute the exact request once and return its result before the originating request completes. For Run, return its complete rows, column names, column types, row count, and column count from that execution. For Check, execute the same read-only SQL to return its validity and exact row and column counts without returning a substituted or estimated result. Do not add a limit or silently truncate rows.
4. Return a SQL error to the originating request as an error, never as an empty successful result. If MCP cannot carry a complete Run result, return an explicit full-result delivery failure. A source-file failure remains an indexer's stderr event, not a query row or query error; this Action does not retry it or write a Journal record.
5. Close the read-only handle when the request completes so the shared owner may hand off to a pending trusted reconciliation. Do not edit Atom sources, update the Projection, request approval, retry, or replay the request.
