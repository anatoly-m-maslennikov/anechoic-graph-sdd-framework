---
identity:
  atom_id: AN-T-1527
context:
  container:
    atom: AN-T-1531
  tier: 3
  template: task
state:
  status: done
  version: 7
  updated_at: 2026-10-25 17:32:27 +0400
---
# Summary

Repair N12 image gate fixtures

## Objective

repair confirmed image-gate fixture or implementation defects against current RMED, preserving real image/canary acceptance.

## Details

- this lane owns 24 failing cases from the frozen N12 Unit report, not a new scope expansion.
- use disposable fixtures; preserve actual Run, runtime, Journal and source snapshot evidence.
- coordinate shared production dependencies instead of overlapping another worker. root integrates accepted changes and current pins.

## Definition of Done

the observed failures are explained and fixed against current authority; focused regression suites pass and independent review accepts the bounded change. actual full Release acceptance remains with the parent Plan.

## Result

- the fixture now reflects the sealed rollback retention condition: `retain_prior` yields a retained prior image and the exact settings condition reference.
- exact immutable-image identity, all-container inspection, rollback selector and command/receipt assertions remain intact.
- the two final regression cases passed in 77.339 seconds with exit 0; independent read-only review accepts the bounded patch.
- the complete N13 Unit gate and later actual Release gates remain required under the parent Plan; the uncaptured long local module run is not claimed passing.
