---
atom_family: TKT
atom_id: AN-T-2996
container:
  atom: AN-T-2973
priority: 2
context:
  template: task
  label: Task
relations:
  IS_REFERENCE:
  - AN-S-3353@1
state:
  status: "done"
  version: 1
  updated_at: "2026-11-22T18:55:53.621928+00:00"
---

## Summary

Detect Python import order failures

## Work

Add eager and deferred import evidence and verify one failing and one
harmless Python cycle.
