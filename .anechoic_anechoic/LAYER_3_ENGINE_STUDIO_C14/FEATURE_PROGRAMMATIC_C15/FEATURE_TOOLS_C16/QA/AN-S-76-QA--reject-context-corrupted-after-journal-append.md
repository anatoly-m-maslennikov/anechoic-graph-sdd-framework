---
identity:
  atom_id: AN-S-76
context:
  container:
    component: C16
  tier: 2
  lens: QA
state:
  status: active
  version: 20
  updated_at: 2026-11-02 19:44:26 +0400
---
## Summary

Reject context corrupted after Journal append

# Reject context corrupted after Journal append

## Claim checked

the commit Doer rejects a sealed context whose canonical fields no longer match the receipt-bound event.

## Test case

Run `APPEND_CHANGE_RECORDS` for one valid `UPDATE`, remove the singular canonical `result` from the context **after** receipts are returned, **and** pass the corrupted context with those receipts **and** the live lease **to** the commit boundary.

## Acceptance criteria

`COMMIT_CHANGE_SET` returns a deterministic context-receipt mismatch diagnostic **before** staging, creates no commit, **and** preserves the accepted Journal records plus one observable blocked action **and** lease state for retry with the original context **or** explicit operator resolution.

## Failure disposition

Reject the Doer **if** it reconstructs the missing field, stages **or** commits, deletes **or** duplicates a Journal record, silently rewrites a receipt, **or** permits a later action **to** bypass the blockage.
