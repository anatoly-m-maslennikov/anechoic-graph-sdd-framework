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
  status: draft
  version: 8
  updated_at: '2026-11-13T22:31:32.702691+00:00'
---
## Summary

Verify native cached query grid pages

## Claim

### Prose Claim

Against real DuckDB materialized results and the MCP boundary, verify `query_page` and applicable `view_fetch`. Zero-based grid indices address original positions despite duplicate or dotted aliases. Public `rowid` order comes from a hidden snapshot ordinal. CTE, DuckPGQ and preview execute original SQL once through the same ordinal CTAS. Original SQL is retained for execution and Bookmark but omitted from ordinary Run and Page responses.

Verify native ordered sorts with `NULLS LAST` and stable ties; literal case-insensitive `contains` where `%` and `_` are not wildcards; conjunctive filters; original whole-cache column metadata; and single-column group page records with global filtered counts across page splits. Invalid grid keys, shapes, operators, directions, indices or types return an input error without damaging the result identity or a later normal page. Page and fetch use only the retained table, with no replay or second cache.

Exercise MCP and native calls, real page boundaries, cache observability and completed exports and explicit inline pages. JSON matrix, CSV and TOON decode to the selected positional values and columns with exact counts and group metadata. Export never reruns SQL.
