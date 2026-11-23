---
atom_family: TKT
atom_id: AN-T-2596
container:
  component: C00
priority: 2
context:
  template: task
state:
  status: archived
  version: 4
  updated_at: 2026-10-24 07:10:22 +0400
---
## Summary

Remove temporal Subject classification authority

# Remove temporal Subject classification authority

the Assignee **must** remove the mandatory temporal Subject axis from model content.

## Scope

(selected RMEDO Claims about CONTINUANT **and** OCCURRENT **in** CORE_META_MODEL at `.anechoic_framework/00_APPLICABLE_METHODOLOGY/000_APPLICABLE_MTHD_sources/001_CORE_META_MODEL`); the source **and** lifecycle admission boundary established by CA-P-976 applies; historical versions, generated copies, runtime, Implementation code, **and** other CAP Atoms are excluded.

## Definition of Done

the Task is **not** Done **if** ((current selected authority still requires CONTINUANT **or** OCCURRENT classification) **or** (removal also loses GOVERNS **or** DEPENDS_ON meaning **or** a distinct target) **or** (the removed axis is replaced by another mandatory redundant invariant/process axis) **or** (executions are conflated with reusable definitions)).

## Details

remove **or** replace the governing definitions, Methods, checks, **and** D specifications of this axis. this phase changes authoritative content; the actual Subject frontmatter migration is deliberately deferred **to** sub-Epic 3. preserve exactly one governed target under the accepted one-Claim authority; identical duplicate targets across old buckets **may** be consolidated **only** losslessly, while different targets require explicit reconciliation. preserve history rather than rewriting archived versions.

execute **only** **after** the explicit prerequisite is Done. **if** confidence **in** a decision is below the effective Autonomous Confidence Threshold, check Project Principles first **and** ask the Operator **if** uncertainty remains; do **not** silently select a new design. no migration is executed merely by creating this Task.
