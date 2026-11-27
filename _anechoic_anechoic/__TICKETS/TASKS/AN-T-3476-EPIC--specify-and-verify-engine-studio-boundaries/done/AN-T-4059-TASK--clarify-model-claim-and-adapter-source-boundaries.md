---
atom_family: TKT
atom_id: AN-T-4059
container:
  atom: AN-T-3476
priority: 2
context:
  template: task
  label: Task
state:
  status: done
  version: 1
  updated_at: '2026-11-27T11:26:53+00:00'
---

## Summary

Clarify Model Claim and Adapter source boundaries

## Acceptance

Distinguish C15 compiled blocks from statement count and cover a
selected Python fence with zero statements. Clarify C30's guarded
read, offline reader, framing and Journal promises. Verify the C30
boundary locally and leave C83/C95 provenance work to AN-T-4062.

## Evidence

C15 now distinguishes an accepted empty block from an unsupported
fence and from blocks with statements. All eight compiler-consumer
tests passed. Its revised formal trace translates and compares in
Lean.

C30 states separate guarantees for guarded reads, offline Spec reads,
TOML, Journal and pure framing. Nineteen Journal checks passed,
including a partial batch with a later unattempted row. Three framing
tests validated 134 generated cases and the historical defect control.
