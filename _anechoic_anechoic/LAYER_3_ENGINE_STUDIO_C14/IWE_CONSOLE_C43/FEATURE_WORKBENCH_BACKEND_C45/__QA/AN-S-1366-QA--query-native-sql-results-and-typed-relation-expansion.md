---
atom_family: SPEC
atom_id: AN-S-1366
container:
  component: C45
tier: 5
context:
  lens: QA
relations:
  IS_REFERENCE:
  - AN-S-3116@1
  - AN-S-1373
state:
  status: active
  version: 19
  updated_at: '2026-11-20T16:34:57.901983+00:00'
---
## Summary

Query native SQL results and typed relation expansion

## Claim scope

Native SQL and typed relation expansion over derived Projection rows.

## Claim

### Prose Claim

Native DuckDB and DuckPGQ SQL/PGQ return requested columns/types/counts and complete rows through stable bounded pages. Typed reachability follows materialized direct/declared-derived Relations once, terminates cycles, and neither infers prose links nor synthesizes a second inverse; Atom and Scope Unit traversal uses its existing source tables. The enabled Realization Graph uses `import_nodes` and its import and test edges.

## Details

Verify native selections, joins, CTEs, aggregation, ordering, regex and GRAPH_TABLE/MATCH with declared dotted Content columns, exact counts and stable pages. Whole-query admission retains comments, quotes, dollar quotes and CTEs; cursor metadata never selects SQL. Preview uses native `relation.limit(N)`, preserves existing LIMIT and changes execution counts; no preview adds no cap. Ordinary responses omit exact SQL, while explicit Bookmark load returns it; save follows successful execution, failed execution saves nothing, and failed post-result save returns partial metadata without retry/rollback.

Verify Run/Check/Page and MCP/web parity: Check has metadata/errors only; Page reuses the same cache; saved Views and legacy saved items retain compatibility; query schema reads no SQL/saved item. Default complete export is JSON matrix; CSV/official TOON preserve duplicate aliases, zero rows, null/empty/typed values and multiline Unicode/Formal Claims. Explicit inline pages match exports and View Run stays metadata-only until fetch. Export failure preserves a known result for later fetch and never reports a failed path or reruns SQL. Query logs retain metadata, never result rows/files.

### Disk-backed Workbench and explicit rebuilds

- Use a disposable Project with a real DuckDB file.
- Verify that startup reuses unchanged source data and parsed imports.
- Add, edit, move, and delete sources while Workbench is stopped.
- Compare SQL tables and DuckPGQ edges after reopening.
- Disable the Realization Graph. Verify that its tables and labels are unavailable.
- Rebuild one table and all tables through Workbench, Console, and MCP.
- Check dependent tables, views, and graph registration for each rebuild.
- Verify that invalid targets fail before writes and produce stderr and a response.
- Verify disk-backed rows, stable pages, expiry, and startup cleanup.
- Verify that live results keep the source snapshots they need.
- Verify that rebuild uses the last executed SQL and effective options.
- Page the replacement result with its new ID after an affected source table rebuilds.
- Check the returned ID map and transfer of View bindings and pins.
- Check that unsynced View SQL stays intact.
- Verify that rebuild repeats neither save nor export.
- Force a failure after graph registration may have changed.
- Verify stderr, the HTTP or MCP error response, and SQL rollback.
- Verify that query serving requires an explicit restart after that failure.
- Start a second writer and verify that it exits with an explicit lock error.
