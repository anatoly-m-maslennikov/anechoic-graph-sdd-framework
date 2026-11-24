---
atom_family: TKT
atom_id: AN-T-2963
container:
  atom: AN-T-2959
priority: 2
context:
  template: task
  label: Task
state:
  status: done
  version: 1
  updated_at: "2026-11-21T20:44:38.493332+00:00"
---
## Summary

Refine MCP lifecycle operations and verify the packaged runtime

## Work

After Header migration, expose the backend lifecycle methods through MCP.
Cover Ticket Asset creation, SPEC Template creation and promotion, and
SPEC Draft archiving. Preserve the Task Template and navigation labels.
Return saved references and paths, or actionable errors.

Verify these operations, invalid inputs with no writes, and Workbench
query visibility in the packaged runtime.
