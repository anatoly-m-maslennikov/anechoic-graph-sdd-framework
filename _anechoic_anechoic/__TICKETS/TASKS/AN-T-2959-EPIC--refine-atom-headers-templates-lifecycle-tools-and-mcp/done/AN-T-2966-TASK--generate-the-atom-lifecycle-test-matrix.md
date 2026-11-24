---
atom_family: TKT
atom_id: AN-T-2966
container:
  atom: AN-T-2959
priority: 2
context:
  template: task
  label: Task
state:
  status: done
  version: 1
  updated_at: "2026-11-21T20:54:06.112481+00:00"
---
## Summary

Generate the Atom Lifecycle test matrix

## Work

Generate cases across every lifecycle route, Atom family, admitted Template,
source situation, and containment state. Cover new Atoms, Current Atoms,
existing Drafts, and Archived revisions. Include attached and detached
Atoms, with ancestors and descendants where containment affects the route.

For each combination, assert the supported result and exact effects or
the expected rejection with zero writes. Check Header, status, version,
reference, derived path, containment, and Workbench visibility where the
operation changes them. Keep the same cases available to static project
testing and to the MCP integration checks that reuse them.

Use named parameters and shared small fixtures so failures identify the
route, family, Template, source situation, and containment state.
