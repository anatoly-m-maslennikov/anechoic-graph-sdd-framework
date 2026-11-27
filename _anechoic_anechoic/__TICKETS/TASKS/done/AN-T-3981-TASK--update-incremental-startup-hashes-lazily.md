---
atom_family: TKT
atom_id: AN-T-3981
container:
  component: C71
priority: 2
context:
  template: task
  label: Task
state:
  status: done
  version: 1
  updated_at: '2026-11-26T09:25:00Z'
---

## Summary

Update incremental startup hashes lazily

## Work

Use carrier hashes for incremental startup. Record admitted path changes in the generation transaction. Fold them into the startup checkpoint in the background while Studio runs. Keep unfinished updates across restart.

## Acceptance

A warm restart reconciles files changed, reverted, moved, or deleted after the last checkpoint. An addressed live change does not load or rewrite the full checkpoint.

## Verification

The running Kernel folded an admitted change in the background. Restart tests retained a pending digest across shutdown and detected a reversion. The runtime reused the same database and reconciled offline edits, moves, additions, and deletions.

[AN-T-3979](../../ISSUES/AN-T-3979-PROBLEM--bound-ticket-status-context-memory-on-full-projects.md)
