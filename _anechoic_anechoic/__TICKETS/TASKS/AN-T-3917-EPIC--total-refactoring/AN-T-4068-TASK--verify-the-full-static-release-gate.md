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

The 2026-11-27 locked Static run exited 1 on the working checkout.
Ruff lint, Ruff format, line length, and 45/300 still fail. The
bytecode check found 454 ignored cache directories outside
`.anechoic_tmp`. TypeScript, Mypy, Source Language, and both import
checks passed.

Focused checks passed for the affected files. The Static test-module
check is still blocked by two source comment findings in Model
Generator. An exact sealed candidate remains pending.
