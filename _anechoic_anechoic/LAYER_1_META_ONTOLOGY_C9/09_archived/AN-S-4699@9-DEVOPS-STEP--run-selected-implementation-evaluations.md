---
atom_family: SPEC
atom_id: AN-S-4699
container:
  component: C9
tier: 3
context:
  template: step
  lens: DevOps
state:
  status: archived
  version: 9
  updated_at: 2026-10-26 05:59:45 +0400
---
## Summary

Run selected implementation Evaluations

# Summary

Run selected implementation Evaluations

## Operation

This Step invokes CA-O-020 in Integrated context with the exact candidate, selected checks/commands, current R/E/D and complete M bindings, Project Principles, complete test inputs and fixtures, permissions, execution phase, and retained issue and regression evidence. Bind the existing selected Plan, or bind the actual admitted in-session P/task with its instruction, Definition of Done, and source context. If CA-O-020's selected P/Plan input is not actually satisfied, return `blocked`; never invent a Plan Atom ID or weaken CA-O-020.

Retain actual output, failed/blocked/unevaluated/stale results and candidate bindings. Return CA-O-020's `passed`, `failed`, or `blocked` result unchanged. No diagnosis, edit, expectation change, retry, or repair.

## Details

`blocked` is terminal unresolved with evidence retained; `passed` and `failed` route through the Workflow's explicit transitions.
