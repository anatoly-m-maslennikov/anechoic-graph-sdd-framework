---
atom_family: SPEC
atom_id: AN-S-1373
structure:
  container:
    component: C45
  tier: 7
context:
  lens: QA
state:
  status: draft
  version: 6
  updated_at: '2026-11-14T00:32:48.561052+00:00'
---
## Summary

Verify cached result lifecycle

## Claim

### Prose Claim

Verify cached result lifecycle with actual Workbench queries, Views, expiry,
and native DuckDB table inspection. Use actual runtime evidence.

## Details

- Query-result files serve delivery only. They carry no cache, restore, or pin state.
- Verify that the result lifecycle adds no settings writes, staging, or restore path.

### Admission and rerun

- Reject multi-statement SQL. Invalid structured Run or View requests leave
  the last result reachable.
- Editing SQL alone preserves the last result.
- An admitted View rerun releases the old result even when SQL fails.

### Retention

- Open Views pin results beyond TTL. Closing keeps young results reachable
  and allows old unpinned results to expire.
- Verify a one-second TTL after explicit restart.
- Restart clears result tables and IDs.

### Delivery failures

- First-page `NaN` or infinity conversion failure leaves no ID,
  registration, or table.
- Later-page conversion failure preserves the known ID for other fetches.
- Export failure returns the known ID and delivery error without a path
  and leaves valid later fetches possible.
- Partial files never count as complete.
