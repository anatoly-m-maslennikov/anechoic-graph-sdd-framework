---
atom_family: TKT
atom_id: AN-T-2279
structure:
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

Repair N12 golden receipt fixtures

## Concern

three Release E2E/Full Gate unit modules fail while verifying the shared golden receipt fixture.

## Evidences

the retained actual N12 JUnit report contains 17 failing cases in this lane. N12's later source-currentness refusal does not invalidate those frozen test observations or establish their cause.

## Blast radius

the declared Unit modules and their shared source-complete fixture or implementation. no actual E2E, image or release acceptance is inferred from mock results.

## Decision

repair the source-complete golden fixture and affected tests without weakening actual receipt, currentness or Full Gate checks.

## Result

the fixture now writes the exact context-derived unit-deadline.json snapshot consumed by the real reader. independent review accepts the two-line fixture change. four focused tests have retained exit-0 terminal results: two retained-fixture cases, the E2E fixed-command/bound-receipt case and the Full Gate exact-partition/unchanged-bytes case. the long combined run has no retained aggregate verdict and is not claimed passing; the fresh complete Unit and later release gates remain with the parent Plan. retain all frozen N12 evidence.
