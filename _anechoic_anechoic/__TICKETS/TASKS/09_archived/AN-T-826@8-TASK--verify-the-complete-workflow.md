---
atom_family: TKT
atom_id: AN-T-826
container:
  component: C14
priority: 2
context:
  template: task
state:
  status: archived
  version: 8
  updated_at: 2026-10-24 09:34:50 +0400
---
## Summary

Verify the complete Workflow

# Summary

Verify the complete Workflow

## Objective

Verify the runnable Engine implementation Workflow through the new Tools on an isolated representative target.

## Details

Integrate the Steps through existing orchestration and Tool discovery/MCP interfaces. Each main runtime Step uses its own subagent; M/E/D preparation may run in parallel with disjoint outputs. Exercise a successful R-to-tests-to-implementation path, a projection conflict/gap path, a missing-new-Tool path and an Implementation-discovered issue. Include parent-owned targeting Requirements, descendant inclusion, Query-only/incomplete source data, an unavailable Scope Unit producer, unconfirmed projection/report storage, and E-case creation that returns errors/unknown effects or lacks evaluation_for. Each must stop affected work without false coverage or completion. Check all selected Rs are accounted for and that final test outcomes are actual, not inferred from source or mocks alone. Reuse functional/integration fixtures; do not make whole-repository cleanup, release or live Subject migration part of this acceptance.

Execute this Task in its own subagent. Preserve unrelated work; the integration owner controls shared files and Git. Split only genuinely oversized own-work into smaller P Tasks before execution. This Task grants no live operation outside the selected implementation scope.

## Definition of Done

Actual new-Tool/Workflow fixtures show complete selected-R coverage, test-first order, truthful issue/block outcomes, fresh subagents and correct saved/Journal reports; source contracts alone do not count as execution.

