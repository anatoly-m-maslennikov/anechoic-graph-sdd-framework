---
atom_family: SPEC
atom_id: AN-S-1371
structure:
  container:
    component: C45
  tier: 8
context:
  lens: QA
state:
  status: active
  version: 6
  updated_at: 2026-11-10 20:47:54 +0400
---
## Summary

Verify native cached query grid pages

## Claim

### Prose Claim

Against real DuckDB materialized results and the MCP boundary, verify `query_page` and applicable `view_fetch`. Zero-based grid indices address original positions despite duplicate/dotted aliases; public `rowid` order comes from a hidden snapshot ordinal. CTE, DuckPGQ and preview execute original SQL once through the same ordinal CTAS; original SQL is retained for execution/Bookmark but omitted from ordinary Run/Page responses.

Verify native ordered sorts with `NULLS LAST` and stable ties, literal case-insensitive `contains` where `%`/`_` are not wildcards, conjunctive filters, original whole-cache column metadata, and single-column group page records with global filtered counts across page splits. Invalid grid keys/shapes/operators/directions/indices/types return input error without damaging the result identity or a later normal page. Page/fetch uses only the retained table: no replay or second cache.

Exercise MCP plus native calls, real page boundaries, cache observability and completed exports/explicit inline pages. JSON matrix/CSV/TOON decode to the selected positional values/columns with exact counts/group metadata; export never reruns SQL.
