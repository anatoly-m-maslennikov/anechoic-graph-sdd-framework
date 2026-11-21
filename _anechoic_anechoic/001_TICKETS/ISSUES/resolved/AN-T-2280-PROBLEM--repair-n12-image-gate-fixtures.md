---
atom_family: TKT
atom_id: AN-T-2280
container:
  component: C16
priority: 2
context:
  template: problem
state:
  status: resolved
  version: 2
  updated_at: 2026-10-23 03:14:50 +0400
---
# Summary

Repair N12 image gate fixtures

## Concern

the sealed Unit image-gate module reports 24 failing or errored cases.

## Evidences

the retained actual N12 JUnit report contains 24 failing cases in this lane. N12's later source-currentness refusal does not invalidate those frozen test observations or establish their cause.

## Blast radius

the declared Unit modules and their shared source-complete fixture or implementation. no actual E2E, image or release acceptance is inferred from mock results.

## Decision

repair confirmed image-gate fixture or implementation defects against current RMED, preserving real image/canary acceptance.

## Result

the fixtures now follow the sealed rollback retention policy without weakening image or container identity checks. the final two regressions passed in 77.339 seconds with exit 0 and independent review accepted the patch. the focused repair is complete; complete Unit and actual Release acceptance remain pending under CA-P-1801. retain the frozen N12 report and historical Events.
