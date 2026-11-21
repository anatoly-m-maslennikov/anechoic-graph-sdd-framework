---
atom_family: TKT
atom_id: AN-T-2753
structure:
  container:
    atom: AN-T-2754
  priority: 2
context:
  template: task
state:
  status: backlog
  version: 1
  updated_at: '2026-11-15T17:02:16.350801+00:00'
---
## Summary

Measure and reduce memory retained by Archive parsing

## Objective

Profile Archive parsing and optional Python imports. Update and review RMEDO for any justified changes. Verify whether a short-lived worker reduces retained memory.

## Definition of Done

Compare RAM and query and watcher latency with the disk-backed baseline. Verify worker exit and memory reclamation if adopted. Record the decision and test evidence.
