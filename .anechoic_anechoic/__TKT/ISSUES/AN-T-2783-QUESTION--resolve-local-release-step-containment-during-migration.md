---
atom_family: TKT
atom_id: AN-T-2783
structure:
  container:
    component: C00
  priority: 2
context:
  template: question
state:
  status: active
  version: 1
  updated_at: '2026-11-19T02:58:17.154905+00:00'
---
## Summary

Resolve Local Release Step containment during migration

## Concern

Should the four migrated Local Release Steps name the Workflow Atom as
their direct logical container?

## Details

CA-O-170@11, CA-O-172@15, CA-O-173@17 and CA-O-178@17 author
`part_of` CA-O-164 and keep C27 as their current carrier container.
CA-R-2465 requires one immediate Workflow or Step container.
The native model admits only one direct container.

Proposed disposition: use the migrated Workflow as direct logical
container. Keep all five active carriers at the flat PMETA root.
Keep the legacy relation and path in the receipt. The four Step-to-Action
`RUNS` bindings were independently verified.
