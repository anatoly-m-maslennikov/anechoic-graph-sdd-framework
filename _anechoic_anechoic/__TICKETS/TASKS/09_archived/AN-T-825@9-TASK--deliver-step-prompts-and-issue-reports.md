---
atom_family: TKT
atom_id: AN-T-825
container:
  component: C14
priority: 2
context:
  template: task
state:
  status: archived
  version: 9
  updated_at: 2026-10-24 09:34:50 +0400
---
## Summary

Deliver Step prompts and issue reports

# Summary

Deliver Step prompts and issue reports

## Objective

Provide the Workflow's short subagent prompts, saved handoffs and issue reporting.

## Details

Each Step gets one fresh subagent, its current inputs, permitted Tool calls, output contract and confidence/permission boundary. Gather/compile outputs are reused by later Steps; no extra full-context preload or reviewer substeps are introduced. Every projection and implementation Step can report issues. Deliver one private Engine run-output writer under the Workflow's own Tool implementation, with its supporting RMED in that owner. No suitable generic projection/report producer is currently bound, so this is explicit work, not an assumed capability. The writer stores R, M, E-policy and D projection files under .anechoic_anechoic/_projection/ENGINE_IMPLEMENTATION/<run_id>/ and one full Run report under .anechoic_tmp/ENGINE_IMPLEMENTATION/<run_id>.md. Reuse the existing private safe-file-write pattern, not the old RMED-review state machine or Atom Create. Validate declared owned locations; reject traversal, absolute/symlink targets and overwriting another Run's output. Verify each write by Readback and return a repository-relative reference before reporting it saved. Preserve original Atom references/Versions and actual current_state evidence, with existing Run/Step/subagent identities, selected R IDs, outcomes, coverage and remaining issues. Reuse workflow_run_support.RunExecutionSession and its existing report_ref/event interfaces for shared Journal linkage; the recorder does not create the output files. Do not add a new public artifact API, source hash scheme or separate Journal. Missing Tool readiness, low confidence or required Operator decisions are explicit blocked outcomes. Do not implement a new retry/recovery subsystem.

Execute this Task in its own subagent. Preserve unrelated work; the integration owner controls shared files and Git. Split only genuinely oversized own-work into smaller P Tasks before execution. This Task grants no live operation outside the selected implementation scope.

## Definition of Done

Prompts are short and self-contained. Fixtures verify the private writer's exact owned outputs and Readback, rejected unsafe/cross-Run writes, fresh-agent handoffs and truthful issue/shared-Journal reports. A returned report_ref without the actual saved file is not completion; no authoritative Atom write or invented creation event is permitted.

