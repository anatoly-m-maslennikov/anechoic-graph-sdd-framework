---
atom_family: TKT
atom_id: AN-T-2281
container:
  component: C16
priority: 2
context:
  template: problem
state:
  status: archived
  version: 1
  updated_at: 2026-10-06 18:24:00 +0000
---
## Summary

Repair N12 sealed suite fixtures

# Summary

Repair N12 sealed suite fixtures

## Concern

two Unit fixtures rely on assumptions not established by the sealed runtime, including an unavailable Git repository at /workspace.

## Evidences

the retained actual N12 JUnit report contains 2 failing cases in this lane. N12's later source-currentness refusal does not invalidate those frozen test observations or establish their cause.

## Blast radius

the declared Unit modules and their shared source-complete fixture or implementation. no actual E2E, image or release acceptance is inferred from mock results.

## Decision

repair source-sealed graph-state and suite fixtures without adding Git metadata to runtime packages or weakening repository/currentness checks.

## Result

the sealed graph fixture passes 14 tests without synthetic Git metadata; the specific sealed-workspace mutation test passes in 58.093 seconds and asserts that no .git exists. independent review accepts both test-only changes. no whole-suite or actual release pass is inferred. retain the frozen N12 report and historical Events.
