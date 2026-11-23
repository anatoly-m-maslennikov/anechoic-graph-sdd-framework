---
atom_family: TKT
atom_id: AN-T-2989
container:
  atom: AN-T-2973
priority: 2
context:
  template: task
  label: Task
state:
  status: "done"
  version: 1
  updated_at: "2026-11-22T18:12:18.308897+00:00"
---

## Summary

Follow resolved Realization Graph calls in Lean

## Work

- Reuse Beta Realization Graph Code Unit IDs and resolved call sites.
- Expand supported calls in Lean. Keep the callee's source and state owner.
- Count mutations and observable outputs. Count a returned value only when
  it reaches the action boundary. Leave unsupported calls unresolved.

## Acceptance

Verify a traced callee write, an emitted output, a discarded return, and
an unsupported call. Compare the examples with Python and Node.
