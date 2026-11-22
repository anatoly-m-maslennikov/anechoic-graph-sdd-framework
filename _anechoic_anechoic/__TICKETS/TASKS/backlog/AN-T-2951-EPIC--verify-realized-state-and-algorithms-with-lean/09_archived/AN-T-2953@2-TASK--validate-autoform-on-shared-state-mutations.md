---
atom_family: TKT
atom_id: AN-T-2953
container:
  atom: AN-T-2951
priority: 2
context:
  template: task
state:
  status: archived
  version: 2
  updated_at: '2026-11-21T17:07:21.324234+00:00'
---
## Summary

Validate Autoform on shared-state mutations

## Work

Translate a bounded state transition in Python and JavaScript. Compare aliasing, scope, and post-state with CPython and Node. Use the Epic lifecycle as the Python case.

## Acceptance

Record passing and failing examples with source locations. Report unsupported constructs and any runtime comparison gaps explicitly.

## Pilot evidence

- Autoform revision `2aea8bee73d1` ran with pinned Lean and Joern. Its Python heap suite passed. The Ticket fixture extracted the status selection from `change_ticket_status` and modeled writes in memory. Lean agreed with CPython on three post-states and detected an omitted write.
- JavaScript `let original = [a]` introduced an extra function reference into the translated array. Node returned `2, 7` after the alias write. Lean returned `1, -3`. The empty-array control with explicit `push` passed.
- The Python ambient `ContextVar` probe produced `hole "module-attr:request_context"`. The pilot has no passing read-only channel check.

Keep this Task open for the JavaScript translation mismatch and ambient-channel coverage before enabling lint.
