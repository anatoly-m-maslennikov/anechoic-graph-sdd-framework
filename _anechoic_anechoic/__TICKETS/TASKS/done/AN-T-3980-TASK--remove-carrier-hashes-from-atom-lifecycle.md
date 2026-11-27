---
atom_family: TKT
atom_id: AN-T-3980
container:
  component: C68
priority: 2
context:
  template: task
  label: Task
state:
  status: done
  version: 1
  updated_at: '2026-11-26T09:30:32Z'
---

## Summary

Remove carrier hashes from Atom lifecycle

## Work

Select the addressed carriers without checkpoint digests. Keep Atom identity, version, status, ownership, and guarded file checks. Remove the superseded indexed lookup work.

## Acceptance

The lifecycle query never reads the carrier hash checkpoint. A leaf Ticket status change on a full Project succeeds within the existing memory limit and admits a native delta.

## Verification

On a disposable Project with 53,746 Atoms, MCP changed the leaf Ticket AN-T-3923@1 from In Queue to Done in 2.834 seconds. The query tests run without a checkpoint table. The production release remains pending.

[AN-T-3979](../../ISSUES/AN-T-3979-PROBLEM--bound-ticket-status-context-memory-on-full-projects.md)
