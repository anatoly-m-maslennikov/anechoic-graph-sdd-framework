---
atom_family: TKT
atom_id: AN-T-3488
container:
  atom: AN-T-3476
priority: 2
context:
  template: task
  label: Task
state:
  status: archived
  version: 1
  updated_at: '2026-11-24T23:42:16.000000+00:00'
---
## Summary

Validate formal Manifest boundary declarations

## Work

Validate each formal Manifest by itself for schema well-formedness and consistency within its modeled boundary declarations. Leave all cross-artifact checks to AN-T-3489.

## Acceptance

Validation reports malformed, internally inconsistent, missing, and unresolved Manifest declarations with source links; it does not compare a Manifest to a Contract or Solution.
