---
atom_family: SPEC
atom_id: AN-S-1357
container:
  component: C43
tier: 5
context:
  lens: QA
state:
  status: archived
  version: 3
  updated_at: 2026-11-04 16:59:55 +0400
---

## Summary

Align MCP Run, Check, and simple web query results

## Claim scope

MCP and web results from the shared synchronous connector.

## Claim

### Prose Claim

MCP and web Run, Page and Check must return the same requested data, original column metadata and exact total counts. A Run evaluates SQL once; its pages stay stable across source refresh. The frontend fetches one page at a time and uses shared components for controls and results.

## Details

| Fixture | Expected outcome |
| --- | --- |
| Result larger than the default page | Run returns 100 rows and total counts; Page retrieves the remainder without rerunning SQL or losing rows. |
| Duplicate column aliases and Unicode values | Ordered metadata and positional values remain exact through MCP and web. |
| Query followed by source refresh | The existing query ID keeps its original result; a new Run sees refreshed data. |
| Check over a large result | Exact counts are returned without loading all rows into a Python result list. |
| Invalid SQL, size, offset or query ID | Useful query error; no empty success or retry. |
| Production frontend build | Static Svelte assets load from the Python listener; editor, errors, counts and page controls work. |
| Source error | stderr identifies it; unrelated valid SQL data remains queryable. |
