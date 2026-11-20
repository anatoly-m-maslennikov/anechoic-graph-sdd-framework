---
identity:
  atom_id: AN-T-1666
context:
  container:
    atom: AN-T-1664
  tier: 3
  template: task
state:
  status: backlog
  version: 5
  updated_at: 2026-10-25 17:32:27 +0400
---
# Summary

Diagnose the unstarted selected-workflow dispatch

## Objective

Bound the liveness and deployment-observability gap raised by CA-C-573 without
starting a shared worker, draining unrelated jobs, replaying the canceled Run, or
claiming a software defect or fix.

## Details

At most 15 minutes own work. Inspect the exact queue/cancellation evidence for
`local-release-cleanup-problem-20261021-01`, the stale `worker.json`/
`worker.ready` evidence, and the current applicable worker/deployment authorities.
Use the purpose-built `get_selected_workflow_run` result for this exact Run and
preserve that generic `get_execution_status` is RMED-only. Separate the unstarted
selected-workflow Run from the actual installed Local release and its healthy
production MCP container. Root owns worker process control, Git, Docker, runtime,
and any deployment effect; this Task is read-only planning/diagnosis.

### Definition of Done

Record the exact observed queue state, worker-readiness evidence, applicable
authority, and next bounded action. If the cause remains uncertain, keep CA-C-573
Active and this Task Backlog. No worker start, queue drain, replay, release retry,
or whole-Epic closure is implied.
