---
atom_family: TKT
atom_id: AN-T-2965
container:
  atom: AN-T-2959
priority: 2
context:
  template: task
  label: Task
state:
  status: "done"
  version: 1
  updated_at: "2026-11-21T20:45:02.774460+00:00"
---
## Summary

Archive SPEC Drafts through MCP

## Work

Extend the lifecycle backend and MCP archive operation to support exact SPEC Draft references. Preserve the Draft content and stable Atom ID. Handle revision collisions without overwriting a carrier. Report each original Draft reference, final Archive reference and path, or failure.

Allow the archive workflow to take the exact references returned by query_run without rebuilding the selection by hand. Test a normal archive, a revision collision, and invalid or stale input.
