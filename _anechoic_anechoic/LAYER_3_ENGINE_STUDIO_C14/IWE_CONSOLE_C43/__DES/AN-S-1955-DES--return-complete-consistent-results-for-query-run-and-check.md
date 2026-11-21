---
atom_family: SPEC
atom_id: AN-S-1955
container:
  component: C43
tier: 3
context:
  lens: DES
state:
  status: active
  version: 11
  updated_at: '2026-11-12T13:28:11.127689+00:00'
---
## Summary

Return complete, consistent results for query Run and Check

## Claim scope

The public Run and Check operations for a query over the query Projection.

## Claim

### Prose Claim

Provide synchronous Run, Check and result fetch through the shared backend/MCP/web. Validate one complete query under CA-R-2728; cursor is editor metadata and row preview is non-negative. Materialize each successful Run once and return its ID, ordered column metadata, exact counts and a completed file descriptor by default, or an explicitly requested bounded inline page. Default responses omit result rows and full SQL; explicit inline delivery returns positional rows. A result path appears only after completion.

Direct Run exports the full or preview-capped materialized result. Page and View Fetch return only a bounded page from the same cache and never execute SQL. Preview preserves an existing LIMIT without rewriting SQL, including CTE and GRAPH_TABLE; inline delivery does not create a second executor or cache. Check returns validity, counts or errors only: no rows, file, SQL echo, Bookmark or log. Explicit Load, View-query and log reads may return SQL.

Later save or export failure preserves the completed result and result ID, reports a partial outcome and failed part, and fabricates neither saved identity/path nor retry/rollback. A failed query has no completed result identity. Preserve ordered and duplicate columns, exact counts, and null, empty, Unicode, newline and Formal Claim values. View Run remains metadata-only until fetch; logs, Bookmarks, Views, result files and materialized tables have separate purposes.
