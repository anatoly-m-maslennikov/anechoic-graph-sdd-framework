---
atom_family: TKT
atom_id: AN-T-4045
container:
  atom: AN-T-4039
priority: 2
context:
  template: task
  label: Task
state:
  status: in_queue
  version: 1
  updated_at: "2026-11-26T22:18:31Z"
---
## Summary

Add Console Diagnostics and rebuild actions

## Work

Add a separate Diagnostics tab at the top right of the Console.
Show runtime health, statistics, and available diagnostics.

Provide two backend actions. Rebuild Realization Graph rebuilds the
Realization Graph. Rebuild Project database rebuilds the Project
database from source. Show the state and outcome of each operation.

## Acceptance

Verify the healthy and unhealthy states and their available diagnostics.
Verify that each action requests its intended rebuild and reports
completion or failure.
