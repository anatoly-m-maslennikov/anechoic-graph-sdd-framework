---
atom_family: TKT
atom_id: AN-T-823
container:
  atom: AN-T-827
priority: 2
context:
  template: task
state:
  status: canceled
  version: 10
  updated_at: '2026-11-20T20:06:19.128001+00:00'
---
# Summary

Implement the tests first

## Objective

Provide a Step that implements the agreed E test cases using the applicable M and D projections before Requirement implementation.

## Details

Give its fresh subagent the R projection, E policies/cases, compiled Ms and Ds. Build source-authored golden fixtures and functional/integration tests at useful real boundaries. Mock external dependencies or controlled inputs, not the target Implementation itself. Verify that the tests run and distinguish a genuine unmet Requirement from a broken harness; existing correct behavior may already pass. Report projection defects and missing test inputs immediately. Split large implementation work into bounded P Tasks only when needed, with disjoint file ownership.

Execute this Task in its own subagent. Preserve unrelated work; the integration owner controls shared files and Git. Split only genuinely oversized own-work into smaller P Tasks before execution. This Task grants no live operation outside the selected implementation scope.

## Definition of Done

Executable tests match the E cases and coverage map; their baseline outcomes and harness validity are recorded without claiming an expected baseline failure is completed implementation.

