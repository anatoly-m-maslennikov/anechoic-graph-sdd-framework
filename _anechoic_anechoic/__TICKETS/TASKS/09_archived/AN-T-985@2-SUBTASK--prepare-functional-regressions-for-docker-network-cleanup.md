---
atom_family: TKT
atom_id: AN-T-985
container:
  component: C15
priority: 2
context:
  template: task
  label: Subtask
state:
  status: archived
  version: 2
  updated_at: '2026-10-21T12:06:05Z'
---
## Summary

Prepare functional regressions for Docker network cleanup

# Summary

Prepare functional regressions for Docker network cleanup

## Objective

Resolve the observed isolated Docker network gate failure without affecting the working MCP.

## Details

Read-only existingtests/fixtures mapping for bounded functional regression design: successfulcase cleanup, partialstartupfailure, interrupt, ownership/refusal/protection and realnetwork absence proof. No sourcewrites/tests/Docker/MCP/release/Git. Return smallest disjoint testownership proposal and exactacceptance; root freezes aftersourceevidence. No unit-test scaffolding for unrequestedgenericcleanupframework.

### Actual result and next boundary

Read-only regression design accepted: existing fixture cleanup checks cover normal/partial startup and cleanup failure; runtime stop retention remains protected. No speculative fixture rewrite or generic cleanup owner is needed for this observed historical capacity issue. P2541 will use the existing real three-test Docker module on an isolated current-source image and compare exact network/production baselines after teardown. Additional cancellation/no-container-start reproduction belongs to C567, separate from current release acceptance.
