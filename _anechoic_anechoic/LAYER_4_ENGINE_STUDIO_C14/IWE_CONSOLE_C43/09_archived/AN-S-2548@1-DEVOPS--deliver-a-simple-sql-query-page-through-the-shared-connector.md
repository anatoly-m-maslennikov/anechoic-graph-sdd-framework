---
atom_family: SPEC
atom_id: AN-S-2548
container:
  component: C43
tier: 4
context:
  lens: DevOps
state:
  status: archived
  version: 1
  updated_at: 2026-11-03 23:17:14 +0400
---

## Summary

Deliver a simple SQL query page through the shared connector

## Claim scope

The local web representation of DuckDB Projection queries.

## Claim

### Prose Claim

The existing application must deliver one small query page with a SQL text area, Check and Run buttons, row and column counts, ordinary result rows, and query errors. Check shows validity and exact counts or the query error; Run shows ordinary result rows and their counts.

The page must use the same SQL connector as MCP. It must stay within the existing local server boundary and must not add a second query evaluator, web service, renderer, or custom TABLE, DOC, or TREE result view.

