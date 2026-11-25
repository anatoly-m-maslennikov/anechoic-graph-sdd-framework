---
atom_family: TKT
atom_id: AN-T-3946
container:
  atom: AN-T-3476
priority: 2
context:
  template: task
  label: Task
state:
  status: done
  version: 1
  updated_at: '2026-11-25T22:10:56+00:00'
---
## Summary

Pilot independent validation of C46 current reply ordering

## Work

Use the pinned C46 Manifest, Contract, and Solution. Derive the
current-reply ordering requirement independently of the lowering
code. Check the actual emitted trace artifact.

## Acceptance

The correct artifact passes. A compiling artifact that allows
display before the current reply fails. Preserve the exact source
pins and the minimized counterexample.
