---
identity:
  atom_id: AN-T-2443
context:
  container:
    component: C16
  template: problem
state:
  status: resolved
  version: 3
  updated_at: 2026-10-23 01:47:30 +0400
---
# Summary

Reject duplicate E2E testcase identities

## Concern

The actual Driver emits two passing JUnit rows with the same testcase identity and returns zero, violating the exact-once declared-case requirement.

## Evidences

The initial characterization was replaced by an enforcing regression. The focused real Driver suite now has seven passing cases and one expected RED: duplicate (classname, name) identities return zero rather than non-passing. No Docker or fabricated Driver XML was used.

## Blast radius

P1751 behavioral acceptance and the separately admitted Candidate E2E/Full Gate boundary. Real Docker and runtime installation remain separately unproved.

## Disposition

Reject duplicate observed testcase identities before a passing Driver outcome. Keep all actual unittest.TestResult observations and terminal outcomes; do not exclude or silently deduplicate cases.

## Resolution

The Driver records repeated observed (classname, name) identities as terminal JUnit errors and exits nonzero. Eight actual unittest-to-JUnit Driver cases pass after the enforcing duplicate-case RED; no case is excluded or silently deduplicated. Independent bounded source review accepts the repair. Root's combined context, Driver and phase-map run passes 24/24; five Runtime binding tests and two actual MCP transport tests also pass separately. Code is saved in 5e0dfee93. This resolves only the named defect; actual Docker E2E and whole Full Gate acceptance remain unfinished.
