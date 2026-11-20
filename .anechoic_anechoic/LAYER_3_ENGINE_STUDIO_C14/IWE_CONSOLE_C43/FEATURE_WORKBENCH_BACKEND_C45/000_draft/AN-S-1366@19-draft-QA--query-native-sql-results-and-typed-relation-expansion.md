---
identity:
  atom_id: AN-S-1366
context:
  container:
    component: C45
  tier: 5
  lens: QA
state:
  status: "draft"
  version: 19
  updated_at: "2026-11-20T13:05:31.238025+00:00"
---
## Summary

Query native SQL results and typed relation expansion

## Claim scope

Native SQL and typed relation expansion over derived Projection rows.

## Claim

### Prose Claim

Native DuckDB and DuckPGQ SQL/PGQ return requested columns/types/counts and complete rows through stable bounded pages. Typed reachability follows materialized direct/declared-derived Relations once, terminates cycles, and neither infers prose links nor synthesizes a second inverse; Atom and Scope Unit traversal uses its existing source tables. When the Import Graph is enabled, `import_nodes` and `import_edges` supply its vertices and edges in the same property graph.

## Details

Verify native selections, joins, CTEs, aggregation, ordering, regex and GRAPH_TABLE/MATCH with declared dotted Content columns, exact counts and stable pages. Whole-query admission retains comments, quotes, dollar quotes and CTEs; cursor metadata never selects SQL. Preview uses native `relation.limit(N)`, preserves existing LIMIT and changes execution counts; no preview adds no cap. Ordinary responses omit exact SQL, while explicit Bookmark load returns it; save follows successful execution, failed execution saves nothing, and failed post-result save returns partial metadata without retry/rollback.

Verify Run/Check/Page and MCP/web parity: Check has metadata/errors only; Page reuses the same cache; saved Views and legacy saved items retain compatibility; query schema reads no SQL/saved item. Default complete export is JSON matrix; CSV/official TOON preserve duplicate aliases, zero rows, null/empty/typed values and multiline Unicode/Formal Claims. Explicit inline pages match exports and View Run stays metadata-only until fetch. Export failure preserves a known result for later fetch and never reports a failed path or reruns SQL. Query logs retain metadata, never result rows/files.

### Disk-backed Workbench and explicit rebuilds

Use a disposable Project with a real DuckDB file. Verify startup reuse for unchanged sources and parsed imports. Add, edit, move, and delete files while Workbench is stopped. Compare the SQL tables and DuckPGQ edges after reopening. Disable the Import Graph and verify the retained import tables and graph labels are unavailable.

Rebuild one table, then all tables, through the owner operation. Check the dependent views and graph in each case. After a single source-table rebuild, page an existing result. Verify disk-backed result rows, stable pages, expiry, startup cleanup, and replacement IDs for live results rebuilt from their retained Run inputs. Force a rebuild failure and verify stderr and no partial publication.

## References

[Disk storage Decision AN-S-3116](./AN-S-3116@1-draft-DES-DECISION--store-native-workbench-duckdb-data-on-disk.md), [Cached result lifecycle AN-S-1373](../QA/AN-S-1373-QA--verify-cached-result-lifecycle.md)
