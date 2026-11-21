---
atom_family: TKT
atom_id: AN-T-2955
container:
  atom: AN-T-2951
priority: 2
context:
  template: task
state:
  status: backlog
  version: 1
  updated_at: '2026-11-21T15:51:42.202313+00:00'
---
## Summary

Verify a selected Python algorithm with PastaLean

## Work

After the State Analyzer stage, translate a small Python algorithm and check one Spec property in Lean. Use transitive dependency selection for rebuild as the first candidate.

## Acceptance

Compare the translated behavior with CPython. Verify the property or record a concrete counterexample. Report unsupported code and open proof obligations separately.
