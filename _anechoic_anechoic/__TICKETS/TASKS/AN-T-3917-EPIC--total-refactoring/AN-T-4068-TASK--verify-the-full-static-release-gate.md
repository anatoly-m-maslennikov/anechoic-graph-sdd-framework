---
atom_family: TKT
atom_id: AN-T-4068
container:
  atom: AN-T-3917
priority: 2
context:
  template: task
  label: Task
state:
  status: in_queue
  version: 1
  updated_at: '2026-11-27T12:46:01+00:00'
---

## Summary

Verify the full Static release gate

## Acceptance

Verify AN-T-4065 through AN-T-4067 together on one exact candidate
using the locked environment. Require the normal full-checkout
Static command and Realization Graph to pass with all required
checks enabled. Record the candidate and evidence before
continuing the authorized Local Release.

## Progress

The locked working-checkout Static run still fails on the remaining
source findings. TypeScript, Mypy, and bytecode checks passed. The
integrated focused run passed 51 tests, and the final focused run
passed seven tests. An exact sealed candidate remains pending.
