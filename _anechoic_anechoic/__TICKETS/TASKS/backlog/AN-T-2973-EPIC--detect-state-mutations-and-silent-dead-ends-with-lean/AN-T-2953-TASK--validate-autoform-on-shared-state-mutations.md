---
atom_family: TKT
atom_id: AN-T-2953
container:
  atom: AN-T-2973
priority: 2
context:
  template: task
state:
  status: in_queue
  version: 5
  updated_at: '2026-11-22T16:54:37.210481+00:00'
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


## Ordered effect evidence

- The Lean checker flags only the silent canary. The CPython and Autoform
  traces agree on mutation-only, output-only, and write-and-restore paths.
- The current Ticket status-selection slice agrees on the ordered writes for
  three inputs. The model uses in-memory status writes for filesystem effects.
- A bounded ContextVar get/set/reset lowering agrees with two CPython cases.
  General ContextVar translation and JavaScript effect proofs remain open.

## Translation check

- CPython and Autoform agree on two bounded ContextVar observations. Lean verifies the translated post-heaps and rejects the omitted-body control.
- Node and the generated Lean interpreter agree on two aliased-array observations. The Node kernel proof exceeded its timeout. Caller-visible JavaScript post-heap proof stays open.
- A trusted Node fixture verifies the ordered environment write, output, and restoration used by the source analyzer. Dynamic and cross-Module aliases remain unresolved.
