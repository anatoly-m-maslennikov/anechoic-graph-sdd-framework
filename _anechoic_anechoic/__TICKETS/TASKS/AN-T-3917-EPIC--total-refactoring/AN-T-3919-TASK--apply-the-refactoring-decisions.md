---
atom_family: TKT
atom_id: AN-T-3919
container:
  atom: AN-T-3917
priority: 2
context:
  template: task
  label: Task
state:
  status: in_queue
  version: 1
  updated_at: '2026-11-24T16:40:34.256033+00:00'
---
## Summary

Apply the refactoring decisions

## Prerequisite

Start after [AN-T-3918](AN-T-3918-TASK--assess-all-import-violations.md) is Done.

## Work

Apply the decisions in the recorded order. Preserve supported contracts and verify behavior with the relevant tests.

## Acceptance

The whole-Project Realization Graph and import lint report zero import violations, including production imports from `*__tests` packages. The relevant tests pass.
