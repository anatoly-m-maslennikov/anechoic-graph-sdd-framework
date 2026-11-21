---
atom_family: TKT
atom_id: AN-T-2964
container:
  atom: AN-T-2959
priority: 2
context:
  template: task
  label: Task
state:
  status: in_queue
  version: 1
  updated_at: '2026-11-21T18:46:48.642839+00:00'
---
## Summary

Migrate SPEC and TKT carriers to the agreed Header

## Work

After AN-T-2960 establishes the schema and order, migrate SPEC and TKT carriers. Preserve Markdown, stable Atom IDs, exact revision references, and recoverable authored values. Derive filenames and placement from the canonical Header.

Verify representative carriers, account for exceptions, and check Workbench visibility. Finish migration before revising the lifecycle backend or MCP tools.
