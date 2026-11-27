---
atom_family: TKT
atom_id: AN-T-2997
container:
  atom: AN-T-2973
priority: 2
context:
  template: task
  label: Task
state:
  status: done
  version: 1
  updated_at: '2026-11-26T16:39:58.815632+00:00'
---

## Summary

Detect leaked Python context bindings

## Work

Add a bounded ContextVar restoration check with normal-exit and exception-
path fixtures.
