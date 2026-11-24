---
atom_family: TKT
atom_id: AN-T-2998
container:
  atom: AN-T-2973
priority: 2
context:
  template: task
  label: Task
relations:
  IS_REFERENCE:
  - AN-S-3355@1
state:
  status: done
  version: 1
  updated_at: "2026-11-22T18:55:53.644593+00:00"
---

## Summary

Check Python mutable argument defaults with Ruff

## Work

Enable existing Ruff B006 in the Python static phase and verify a mutable
default and a fresh per-call value.
