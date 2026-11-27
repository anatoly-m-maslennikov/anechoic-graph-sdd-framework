---
atom_family: TKT
atom_id: AN-T-4013
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

Queue Archive changes during background load

## Work

Load Current and Draft Atoms first. Scan Archive filenames for each
distinct Atom ID and its maximum version. Load Archived Atom content
in a background Worker. The watcher adds Archive events to the normal
queue. Apply them after the initial Archive load. Keep lifecycle
writes on the existing direct Kernel admission path.

## Acceptance

Verify that foreground readiness does not wait for Archive content.
Verify maximum-version allocation and existing collision handling
while the Archive load is pending. Verify that queued adds, moves,
deletes, and edits apply after the load. Skip a stale queued item whose
source changed or vanished without failing the job. A newer queued
event still applies. Use AN-T-4012 evidence to assess watcher memory.
