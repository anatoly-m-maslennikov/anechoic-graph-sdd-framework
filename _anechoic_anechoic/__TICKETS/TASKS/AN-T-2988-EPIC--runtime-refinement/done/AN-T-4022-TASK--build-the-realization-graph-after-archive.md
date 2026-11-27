---
atom_family: TKT
atom_id: AN-T-4022
container:
  atom: AN-T-2988
priority: 2
context:
  template: task
  label: Task
state:
  status: done
  version: 1
  updated_at: "2026-11-26T20:12:21Z"
---

## Summary

Build the Realization Graph after Archive

## Work and acceptance

Start automatic Realization Graph work after the initial Archive job
settles. Keep Studio readiness and Model-derived Atom relations on
their existing paths.

Verify that Graph waits while Archive work is active and starts when
Archive completes or fails. Cover Projects with no Archive work.

## Verification

Nine focused tests passed. They cover active Archive work, a queued
reconciliation, a reconciliation consumed with an explicit build,
Archive completion and failure, and no Archive work. An already
running Graph can finish. Production files passed the 300/45 limits.

The broader Archive test run still has two mismatched expectations
for the separate Model rebuild argument.
