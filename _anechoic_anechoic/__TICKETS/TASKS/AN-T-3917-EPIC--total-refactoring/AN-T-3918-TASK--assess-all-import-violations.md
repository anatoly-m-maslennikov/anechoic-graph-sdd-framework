---
atom_family: TKT
atom_id: AN-T-3918
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

Assess all import violations

## Work

Use the whole-Project Realization Graph and import lint to inventory every import violation. Include production imports from `*__tests` packages (`code_access_findings` with reason `non-test import from Test Package`).

For each affected scope, choose a rewrite from the ground up or a targeted fix. Record a brief reason and the order of work.
