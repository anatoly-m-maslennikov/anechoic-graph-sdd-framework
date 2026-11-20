---
identity:
  atom_id: AN-T-1562
context:
  container:
    atom: AN-T-1578
  tier: 3
  template: task
state:
  status: done
  version: 9
  updated_at: 2026-10-25 17:32:27 +0400
---
# Summary

Repair Base Revise prompt and fixture drift

## Objective

Align the current compact Base Revise prompts, source pins and test fixtures with accepted local checks.

## Details

RMED_ATOM_REVIEW prompt tree and tests; rmed_prompt_drift_repair. Preserve gather/check/fix, no workflow recheck, replacement authorization and the current word budget.

Estimated bounded slice: <=15 minutes. Workers share the checkout, preserve other edits and do not stage or commit. Root owns integration and Git. Preparation does not prove runtime execution.

## Definition of Done

Current source pins and prompt budgets validate; stale root/layout fixtures are corrected; genuine defects remain explicit rather than skipped.

## Pre-execution review

Root accepts this bounded repair/restoration against Operator authority, DRY, preservation of valuable information and the latest continuation. Keep installed N intact and distinguish local tests from required actual runtime gates.

## Recorded verification

31c46bba5 retains compact current prompts, source pins and fixture corrections. The complete prompt suite passed 372 tests and repair suite 117; layout exception is API-owned, not a self-asserted report marker. No new runtime Run was dispatched.
