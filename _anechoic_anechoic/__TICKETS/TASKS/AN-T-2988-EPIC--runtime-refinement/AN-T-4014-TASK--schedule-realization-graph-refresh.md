---
atom_family: TKT
atom_id: AN-T-4014
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

Schedule Realization Graph refresh

## Work

Check Graph inputs after foreground readiness and every 10 minutes by
default. Skip unchanged inputs. Expose an immediate Graph-only refresh
through the API and MCP using
`query_rebuild(target="realization_graph")`.

## Acceptance

Scheduled and manual refreshes share one short-lived Worker per
Project. Reuse admitted Model and Structure, and keep foreground
readiness and native Atom updates independent of Graph work. Verify
changed and unchanged inputs, overlapping requests, and both entry
points.
