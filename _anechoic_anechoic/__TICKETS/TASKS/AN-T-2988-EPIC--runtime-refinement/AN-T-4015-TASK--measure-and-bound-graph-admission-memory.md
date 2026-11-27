---
atom_family: TKT
atom_id: AN-T-4015
container:
  atom: AN-T-2988
priority: 2
context:
  template: task
  label: Task
state:
  status: in_queue
  version: 1
  updated_at: "2026-11-26T18:36:29Z"
---
## Summary

Measure and bound Graph admission memory

## Work

After AN-T-4012, measure the Worker reply and Kernel admission copies
during a Realization Graph refresh. If the handoff materially increases
Orchestrator memory, reuse the pinned artifact pattern and let Kernel
admit the Worker output from disk.

## Acceptance

Report the measured cost. If the handoff changes, show that
Orchestrator no longer holds the Graph payload and that Kernel rejects
invalid or stale artifacts while keeping the last complete Graph.
