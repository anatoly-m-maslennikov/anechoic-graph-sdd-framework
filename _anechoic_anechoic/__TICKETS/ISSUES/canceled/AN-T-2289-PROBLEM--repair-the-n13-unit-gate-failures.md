---
atom_family: TKT
atom_id: AN-T-2289
container:
  component: C00
priority: 2
context:
  template: problem
state:
  status: canceled
  version: 2
  updated_at: '2026-11-20T20:34:46.078444+00:00'
---
# Summary

Repair the N13 Unit gate failures

## Concern

N13's complete Unit report contains thirty-four failed or errored tests across six modules.

## Evidences

- .anechoic_runtime/release_suite/1945f7bf7b02b8550c04a39b57d6e39ead4a4ea3a45b317f4580a7d0bf3713f3/attempt-1sbz9z4g/coverage.xml: 2,009 testcases, 22 failures, 12 errors and no skips; suite exit 1 after 2441.773051917 seconds.
- the actual Run stopped at the Unit gate and recorded twenty-two Events with no pending recording. no package/image/canary/E2E/promotion/retirement followed.

## Blast radius

the confirmed test fixture/reference-closure defects and any narrowly demonstrated implementation cause; current source, history and installed N remain protected.

## Decision

repair six independently bounded failure groups, obtain focused source-equivalent evidence and independent acceptance, then use a fresh source-bound Run. do not replay N13 or weaken the gate.
