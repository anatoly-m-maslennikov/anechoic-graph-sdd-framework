---
atom_family: TKT
atom_id: AN-T-2980
container:
  atom: AN-T-2977
priority: 2
context:
  template: task
  label: Task
state:
  status: "archived"
  version: 2
  updated_at: "2026-11-22T10:10:31.855796+00:00"
---

## Summary

Use authoritative inputs for Python import resolution

## Objective

Identify the source for ordered Python search paths and previous-image dependencies. Use that authority to remove duplicated configuration from the Project Manifest. Verify graph edges, unresolved imports, and release compatibility.

## Target

Use one Python root. Check the Project root (`.`) as the default. Measure old-root dependencies and preserve previous-image import handling.
