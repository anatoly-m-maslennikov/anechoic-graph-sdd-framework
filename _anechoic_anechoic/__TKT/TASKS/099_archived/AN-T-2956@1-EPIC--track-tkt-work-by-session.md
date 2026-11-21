---
atom_family: TKT
atom_id: AN-T-2956
structure:
  container:
    component: C18
  priority: 2
context:
  template: epic
state:
  status: "archived"
  version: 1
  updated_at: "2026-11-21T16:15:16.147945+00:00"
---
## Summary

Track TKT work by session

## Objective

Give operators a Session Work Log for TKT Atoms and the Workflows that act on them.

## Work

- Specify the Session Work Binding and reuse the Project and session identity from MCP caller context.
- Make the explicit MCP start-work call and a Workflow start on a TKT Atom create the same binding.
- Expose MCP bind, unbind, and list. List defaults to the current session and can include all sessions in the Project.
- Preserve released and completed entries in the log. Complete open bindings after the Atom moves to Done, Canceled, or Archived without a replacement.

## Acceptance

- A session can start work on any eligible TKT Atom and see its binding. Reads leave the log unchanged.
- Unbind releases the binding and retains its history. The Project-wide list identifies each entry's session.
- A confirmed terminal move completes the affected bindings. Archival with a replacement leaves them open.
