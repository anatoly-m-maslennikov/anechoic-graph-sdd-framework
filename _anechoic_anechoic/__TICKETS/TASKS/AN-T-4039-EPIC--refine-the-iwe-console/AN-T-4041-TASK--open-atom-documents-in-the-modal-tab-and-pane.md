---
atom_family: TKT
atom_id: AN-T-4041
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

Open Atom documents in the modal, tab, and pane

## Work

Make Atom IDs clickable throughout the Console. A bare ID opens its
Current version. A versioned ID opens that exact revision.

Use the same full Document view in the modal, in a Console tab, and
in the right pane. Left-click an Atom ID in a result table or Graph to
open the modal. Right-click to show Open in pane and Open in new tab.
Provide both actions in the modal. Opening a new tab switches to it.
Opening in the right pane splits the current tab and adds a collapsible
document below any documents already open there.

Render Document query results as one continuous document in query
order. Each collapsed Atom shows only its clickable canonical filename.
Place Hide all and Expand all below the filters and query.

## Acceptance

Verify all three open destinations from a table and Graph. Verify
exact-revision links and expansion controls. Each full Document view
shows history for all versions, including Archived, Ready, and Draft,
plus lists of related Atoms and contained Atoms.
