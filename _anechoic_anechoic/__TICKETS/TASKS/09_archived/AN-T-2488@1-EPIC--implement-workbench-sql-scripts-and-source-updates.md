---
atom_family: TKT
atom_id: AN-T-2488
container:
  component: C14
priority: 2
context:
  template: task
  label: Epic
state:
  status: archived
  version: 1
  updated_at: 2026-11-11 00:51:59 +0400
---

## Summary

Implement Workbench SQL scripts and source updates

## Objective

Implement the new capabilities adopted by the concurrent source review after completing P2791.

## Scope

The Operator assigned these new capabilities to a follow-up Epic on 11 November 2026. Use the exact Current source handoff at `.anechoic_tmp/p2791-implementation-20261111/source-handoff.md`; refresh versions and hashes before dispatch. SQL scripts, source-backed updates and their Tab/help integration are pending implementation, not P2791 acceptance. Run/history reads, native Codex rendering, standalone chat and retired Tool routes retain their separate deferrals.

## Procedure

Current RMEDO → review/fix → applicable Method Policy prompt → REDO plus non-Policy M → bounded implementation → actual E2E → independent review/fix. One receiving Scope Unit per worker, exclusive paths and batches of at most 15–20 minutes.

## Tasks

- [ ] [Confirm the adopted SQL implementation inputs](CA-P-2912-EPIC--implement-workbench-sql-scripts-and-source-updates/CA-P-2913-TASK--confirm-the-adopted-sql-implementation-inputs.md)
- [ ] [Implement sequential SQL scripts](CA-P-2912-EPIC--implement-workbench-sql-scripts-and-source-updates/CA-P-2914-TASK--implement-sequential-sql-scripts.md)
- [ ] [Implement source-backed SQL updates](CA-P-2912-EPIC--implement-workbench-sql-scripts-and-source-updates/CA-P-2915-TASK--implement-source-backed-sql-updates.md)
- [ ] [Align Tabs with script execution](CA-P-2912-EPIC--implement-workbench-sql-scripts-and-source-updates/CA-P-2916-TASK--align-tabs-with-script-execution.md)
- [ ] [Expose tool-specific generated help](CA-P-2912-EPIC--implement-workbench-sql-scripts-and-source-updates/CA-P-2917-TASK--expose-tool-specific-generated-help.md)
- [ ] [Verify and deliver source-backed query changes](CA-P-2912-EPIC--implement-workbench-sql-scripts-and-source-updates/CA-P-2918-TASK--verify-and-deliver-source-backed-query-changes.md)

## Definition of Done

The accepted in-scope source contracts are implemented and verified through actual interfaces and lifecycle cases without regressing performance or resource limits. Report delivery separately.
