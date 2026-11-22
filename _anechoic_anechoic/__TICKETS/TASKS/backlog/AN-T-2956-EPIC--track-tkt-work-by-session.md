---
atom_family: TKT
atom_id: AN-T-2956
container:
  component: C18
priority: 2
context:
  template: epic
state:
  status: backlog
  version: 2
  updated_at: '2026-11-21T16:15:16.148665+00:00'
---
## Summary

Track TKT work by session

## Objective

Show each Ticket's Assignee and retain assignment history in an Assignment Log. The Assignee is the session doing the work.

## Work

- When a session explicitly starts work on any TKT Atom through MCP, assign it to that session. A Workflow that starts work on the Atom uses the same assignment.
- Reuse the existing session identity from MCP caller context. Reads leave the Assignment Log unchanged.
- Expose MCP assign, unassign, and list assignments. List defaults to the current session and supports all sessions in the Project.
- Unassign releases the assignment and retains its history. Complete open assignments after a confirmed move to Done, Canceled, or Archived without a replacement.

## Acceptance

- The current session and Project-wide lists identify the Ticket, Assignee, and assignment state.
- Done and Canceled moves complete open assignments. Archival completes them only when the Ticket has no replacement.
