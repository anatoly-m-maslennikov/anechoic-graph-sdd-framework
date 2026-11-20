---
atom_family: SPEC
atom_id: AN-S-1366
structure:
  container:
    component: C45
  tier: 5
context:
  lens: QA
state:
  status: draft
  version: 17
  updated_at: '2026-11-13T22:31:27.835926+00:00'
---
## Summary

Query native SQL results and typed relation expansion

## Claim scope

Native SQL and typed relation expansion over derived Projection rows.

## Claim

### Prose Claim

Verify that native DuckDB and DuckPGQ SQL/PGQ return requested columns, types, counts and complete rows through stable bounded pages. Typed reachability follows materialized direct and declared-derived Relations once and terminates cycles. It neither infers prose links nor synthesizes a second inverse. Graph source tables remain `atoms` and `scope_units`.

## Details

Verify native selections, joins, CTEs, aggregation, ordering, regex and GRAPH_TABLE/MATCH with declared dotted Content columns, exact counts and stable pages. Whole-query admission retains comments, quotes, dollar quotes and CTEs; cursor metadata never selects SQL. Preview uses native `relation.limit(N)`, preserves existing LIMIT and changes execution counts. Without preview, no cap is added. Ordinary responses omit exact SQL, while explicit Bookmark load returns it. Save follows successful execution. Failed execution saves nothing. Failed post-result save returns partial metadata without retry or rollback.

Verify Run, Check and Page and MCP/web parity. Check has metadata and errors only; Page reuses the same cache; saved Views and legacy saved items retain compatibility; query schema reads no SQL or saved item. Default complete export is JSON matrix. CSV and official TOON preserve duplicate aliases, zero rows, null and empty and typed values, and multiline Unicode and Formal Claims. Explicit inline pages match exports. View Run stays metadata-only until fetch. Export failure preserves a known result for later fetch, never reports a failed path and never reruns SQL. Query logs retain metadata, never result rows or files.
