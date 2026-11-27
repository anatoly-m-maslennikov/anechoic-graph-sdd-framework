---
atom_family: TKT
atom_id: AN-T-4021
container:
  atom: AN-T-4019
priority: 2
context:
  template: task
  label: Subtask
state:
  status: "done"
  version: 1
  updated_at: "2026-11-26T19:56:51.649671+00:00"
---

## Summary

Load and replace the accepted compiled Model on startup

## Work

Load the accepted Model from the single Project asset. Reuse it when Model inputs match. Compile changed inputs once and replace the file after accepting Model and Structure. Verify unchanged startup, changed input, explicit rebuild, and candidate rejection.
