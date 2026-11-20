---
identity:
  atom_id: AN-S-1373
context:
  container:
    component: C45
  tier: 7
  lens: QA
state:
  status: active
  version: 5
  updated_at: 2026-11-10 20:47:54 +0400
---
## Summary

Verify cached result lifecycle

## Claim

### Prose Claim

Use the real Workbench and native DuckDB result tables to verify whole-query admission rejects multi-statements; invalid structured Run/View preserves the last reachable result; valid failed View rerun releases the old result; and SQL editing alone preserves it. An open View pins beyond TTL, closed young results remain reachable, and old unpinned results may expire. `result_ttl_seconds = 1` takes effect only after explicit Workbench restart.

First-page `NaN`/infinity conversion failure creates no ID/registration/table; later-page failure after a known ID preserves it for other fetches. Restart clears all result tables/IDs. Query-result files are delivery artifacts, not cache/restore/pin state; no setting write/staging/restore path is added. Use actual queries, views, expiry and table observability, not mocks/row lists/frontend state. Export failure returns known ID plus delivery error without a successful path; valid later fetch remains possible and partial files never count complete.
