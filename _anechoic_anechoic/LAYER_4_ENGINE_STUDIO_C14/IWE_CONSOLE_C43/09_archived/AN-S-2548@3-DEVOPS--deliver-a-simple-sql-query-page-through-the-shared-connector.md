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
  version: 3
  updated_at: 2026-11-04 16:35:58 +0400
---

## Summary

Deliver a simple SQL query page through the shared connector

## Claim scope

The local web representation of the in-memory DuckDB Projection.

## Claim

### Prose Claim

The existing application must deliver one small query page with a SQL text area, Check and Run buttons, row and column counts, ordinary result rows, and query errors. Check shows validity and exact counts or the query error; Run shows ordinary result rows and their counts through the shared connector.

The page remains inside the existing local application boundary. It does not add a second query evaluator, web service, renderer, or custom TABLE, DOC, or TREE result view. It need not materialize or display all rows at once, and this Draft defines no UI truncation or pagination policy.


The page is `/anechoic/workbench`; Run and Check use `/anechoic/workbench/run` and `/anechoic/workbench/check` on the same listener.
