---
atom_family: TKT
atom_id: AN-T-3472
container:
  atom: AN-T-3468
priority: 2
context:
  template: task
  label: Task
state:
  status: done
  version: 1
  updated_at: '2026-11-23T23:07:47.000000+00:00'
---
## Summary

Fix the carrier delimiter start position

## Work

In the scoped carrier body Adapter, fix delimiter matching to use the compiled
regular expression with the correct `pos` start position. Preserve exact body
bytes, existing errors, and the current Adapter scope. Re-run the 110
independent Contract cases, including the five previous offset cases and the
proposed in-memory zero-mismatch check.

## Acceptance

The compiled regex receives the intended `pos` value. All 110 independent
Contract cases pass, with exact bodies and errors preserved. Report the five
offset results and the in-memory mismatch count.
