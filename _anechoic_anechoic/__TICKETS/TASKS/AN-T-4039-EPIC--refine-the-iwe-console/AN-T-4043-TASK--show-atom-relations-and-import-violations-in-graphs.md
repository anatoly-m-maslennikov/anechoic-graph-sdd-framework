---
atom_family: TKT
atom_id: AN-T-4043
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

Show Atom relations and import violations in graphs

## Work

At depth 0, draw only the query matches and the edges between them.
Provide a depth input and a Show related button. Each increment adds
one hop of related nodes. Set depth back to 0 to restore the query set.
The Relation types filter starts with all types selected. The filter
controls which edges appear and which relations expansion follows.

Support Atom nodes and an option to include Components and Packages
with their Spec Bindings. Add a separate Imports Graph from admitted
Realization Graph data. Draw violation edges in red. Support vertical
and horizontal layouts.

## Acceptance

Verify depth 0, 1, and 2, relation filtering, both layouts, and visible
Spec Bindings. Verify an import violation appears as a red edge and
that Atom nodes support the normal document-opening actions.
