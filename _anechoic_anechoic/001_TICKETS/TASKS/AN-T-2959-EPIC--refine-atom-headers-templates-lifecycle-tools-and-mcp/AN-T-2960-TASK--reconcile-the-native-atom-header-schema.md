---
atom_family: TKT
atom_id: AN-T-2960
container:
  atom: AN-T-2959
priority: 2
context:
  template: task
  label: Task
state:
  status: in_queue
  version: 2
  updated_at: '2026-11-21T18:58:35.311252+00:00'
---
## Summary

Reconcile the native Atom Header schema

## Work

Finalize the authored YAML Header structure and canonical field order for
SPEC and TKT. Declare common, family-specific, required, and optional
fields in the Active Model. Keep derived values out of the Header.

Confirm the Template-specific rules and verify representative SPEC and TKT
Headers against the agreed schema. Complete this before carrier migration.

## Ticket Concern

Use one optional `concern` list for typed references, such as
`concern: [component(id=C51)]`. Each entry names its target type and ID.
Use this list for different target types. Keep ownership in
`structure.container`. Reserve the `@` prefix for eDSL function calls.
