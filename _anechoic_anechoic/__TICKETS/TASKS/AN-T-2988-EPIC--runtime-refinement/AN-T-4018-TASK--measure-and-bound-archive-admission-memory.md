---
atom_family: TKT
atom_id: AN-T-4018
container:
  atom: AN-T-2988
priority: 2
context:
  template: task
  label: Task
state:
  status: in_queue
  version: 1
  updated_at: "2026-11-26T19:05:24Z"
---
## Summary

Measure and bound Archive admission memory

## Work and acceptance

After AN-T-4016, measure Orchestrator and Kernel memory separately
while the same frozen Project admits its full Archive. Isolate the
Worker reply, parsed snapshot, and Kernel request from Graph work.
If the handoff materially raises memory, reuse the batched artifact
path for Archive admission.

Verify peak memory and that Kernel publishes one complete Archive.
Cover rejection of an invalid artifact or a stale generation.

## Progress

The Archive Worker writes the existing batch format. Orchestrator passes
the artifact pin to Kernel. Kernel decodes and validates full generation
and Archive payloads outside the live lock, then rechecks the Archive
base and publishes in one transaction.

Focused tests cover reads during preparation, stale and invalid input,
and a live update during Archive loading. Measure peak memory and
readiness interruptions on the same Project. Direct staging of each
frame in DuckDB remains in AN-T-3923.
