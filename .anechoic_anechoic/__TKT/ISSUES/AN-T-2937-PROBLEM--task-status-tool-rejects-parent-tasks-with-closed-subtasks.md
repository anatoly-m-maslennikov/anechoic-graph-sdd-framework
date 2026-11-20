---
atom_family: TKT
atom_id: AN-T-2937
structure:
  container:
    component: C16
  priority: 2
context:
  template: problem
relations:
  REFERENCES:
  - AN-T-160
  - AN-S-1616
state:
  status: active
  version: 1
  updated_at: '2026-11-20T20:20:10.229747+00:00'
---
## Summary

Task status tool rejects parent Tasks with closed Subtasks

## Concern

The native status tool rejects a parent Task whenever it owns an Atom or has a companion folder. AN-T-160 reproduces the problem. Its five Subtasks are Canceled, but marking the parent Canceled returns `Direct updates of container Atoms are unsupported.`

## Acceptance

- Allow a parent Task with closed Subtasks to move to Canceled.
- Move its companion folder with it. Preserve closed Subtask statuses, references, and history.
- Cover a nested tree. Apply the containment rules when unfinished Subtasks remain.
