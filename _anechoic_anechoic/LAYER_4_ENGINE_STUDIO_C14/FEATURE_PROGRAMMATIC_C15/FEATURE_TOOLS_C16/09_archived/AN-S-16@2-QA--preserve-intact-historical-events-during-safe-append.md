---
atom_family: SPEC
atom_id: AN-S-16
container:
  component: C16
tier: 4
context:
  lens: QA
state:
  status: archived
  version: 2
  updated_at: 2026-10-23 03:17:34 +0400
---
## Summary

Preserve intact historical events during safe append

# Preserve intact historical events during safe append

## Claim checked

APPEND_CHANGE_RECORDS rejects a damaged sealed event envelope **or** an unsafe append attempt, **not** intact historical evidence merely because the live Project changed.

## Cases

1. gather a sealed event **and** alter a sealed observation field **without** updating its integrity binding.
2. attempt an append against a Journal position invalidated by another accepted append.
3. retain the intact historical event **and** independently advance the Project's Git base **or** change its observed subject **after** capture.

## Acceptance

- case 1 fails event-integrity checks **before** append; the Doer **must not** silently reseal changed facts.
- case 2 obtains a current safe append position **or** returns a storage-conflict result **without** partial append, loss of the pending event, **or** rewritten history.
- case 3 remains recordable as the original historical observation. it does **not** authorize a Project mutation against stale preconditions.
- failed append attempts release unconsumed storage leases **and** preserve the exact pending event for admitted retry.

## Failure disposition

reject the appender Implementation **if** it accepts damaged event data, overwrites accepted records, drops historical evidence because of later Project changes, **or** treats Journal admission as Git mutation approval.
