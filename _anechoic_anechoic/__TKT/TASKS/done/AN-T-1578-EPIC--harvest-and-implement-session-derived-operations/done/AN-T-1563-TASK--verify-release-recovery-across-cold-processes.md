---
atom_family: TKT
atom_id: AN-T-1563
structure:
  container:
    atom: AN-T-1578
  priority: 2
context:
  template: task
state:
  status: done
  version: 8
  updated_at: 2026-10-25 17:32:27 +0400
---
# Summary

Verify Release recovery across cold processes

## Objective

Prove persisted checkpoint and pending-event recovery after a fresh interpreter starts without repeating effects.

## Details

WORKFLOW_ORCHESTRATOR/test_release_recovery_host_restart_e2e.py; restart_recovery_finish. Existing checkpoint/Journal protocol governs. Live N5 and installed N are untouched.

Estimated bounded slice: <=15 minutes. Workers share the checkout, preserve other edits and do not stage or commit. Root owns integration and Git. Preparation does not prove runtime execution.

## Definition of Done

Cold synthetic pre-effect/post-effect/completed/N5-shaped cases pass using actual codecs/recorder. Synthetic evidence is not reported as live Docker release acceptance.

## Pre-execution review

Root accepts this bounded repair/restoration against Operator authority, DRY, preservation of valuable information and the latest continuation. Keep installed N intact and distinguish local tests from required actual runtime gates.

## Recorded verification

75c90cd56 retains four cold-process tests using actual codecs and pending Journal recovery; the combined recovery slice passed 41 cases. Typed synthetic evidence is not actual Release/Docker proof. N5 was untouched and is not a recording-only recovery candidate.
