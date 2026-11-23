---
atom_family: SPEC
atom_id: AN-S-1363
container:
  component: C45
tier: 4
context:
  lens: SWD
state:
  status: archived
  version: 5
  updated_at: 2026-11-05 17:09:51 +0400
---

## Summary

Keep DuckDB Projection ownership in the existing server.

## Claim scope

The derived DuckDB Projection and query results for one Project.

## Claim

### Prose Claim

Keep one serialized DuckDB owner in the existing application. Store its rebuildable database and spill data under `.anechoic_runtime/workbench` in the selected repository. Source files remain authoritative; the database is disposable derived data.

Materialize each Run once. Direct query_run returns a stable query ID, original column metadata, exact total counts and its first page; View Run returns only execution metadata and a query ID, and its rows are fetched separately. Read subsequent pages from that materialized result, including after source refresh. Default to 100 rows per page and allow 1 through 1,000. Reject invalid sizes, offsets and unknown IDs explicitly. No hidden row limit changes the query result.

Keep reachable materialized Run results until their View replaces/removes them or the owner closes. If first-page conversion fails before the caller receives a query ID, remove that result registration and cache table before returning the error. A later page-conversion error keeps the caller's known result ID available for other pages. Rebuild the Projection and clear old query results at startup; result IDs do not survive restart. Check counts without transferring all result rows to Python and discards its own materialized result.

Serialize source refresh, Run, Page and Check through the same owner. Requests remain synchronous. Do not add a database server, queue, planner, scheduler, orchestrator or background query worker. Release successful parsed-source caches after refresh; retain failed-source signatures so unchanged invalid inputs are not retried.
