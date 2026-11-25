---
atom_family: TKT
atom_id: AN-T-3012
container:
  component: C43
priority: 2
context:
  template: problem
state:
  status: in_queue
  version: 1
  updated_at: '2026-11-23T05:28:19.388245+00:00'
---
## Summary

Workbench browser storage fallback can fail the Local Release image gate

## Claim

### Prose Claim

The 0.4.4.77 Local Release passed 20 static tests and 552 host unit tests. The packaged image gate failed only `standalone-url.e2e.spec.ts:47` when the browser forced `localStorage.setItem` to throw. The query result column for `SELECT 7 AS in_memory` did not appear.

AN 3 ran the exact case in fresh canaries for both Architecture Analysis and Workbench. Both passed on the first attempt. The complete image gate failure remains unexplained.

## Verification

Capture the failed browser run's query dispatch, API response, and browser console. Restore a passing full Local Release image gate.
