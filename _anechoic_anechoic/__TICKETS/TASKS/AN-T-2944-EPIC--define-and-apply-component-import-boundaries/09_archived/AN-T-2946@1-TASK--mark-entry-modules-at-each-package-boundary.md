---
atom_family: TKT
atom_id: AN-T-2946
container:
  atom: AN-T-2944
priority: 2
context:
  template: task
state:
  status: archived
  version: 1
  updated_at: '2026-11-21T12:15:27.066352+00:00'
---

## Summary

Mark entry Modules at each Package boundary

## Work

Apply AN-S-3179 to the direct code files of each Package. Prefer one `__family_pub` Module for the Package itself, its immediate parent, and its immediate siblings. Add a `__pub` Module when the Package exposes a public Contract. Keep unmarked code Package-local. Check each child Package separately and preserve explicit Spec exports.
