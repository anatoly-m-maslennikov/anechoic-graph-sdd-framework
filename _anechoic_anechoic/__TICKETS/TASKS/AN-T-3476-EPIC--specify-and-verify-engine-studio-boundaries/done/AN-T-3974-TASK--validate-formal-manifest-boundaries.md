---
atom_family: TKT
atom_id: AN-T-3974
container:
  atom: AN-T-3476
priority: 2
context:
  template: task
  label: Task
state:
  status: done
  version: 2
  updated_at: '2026-11-25T13:10:19+00:00'
---
## Summary

Validate formal Manifest boundary declarations

## Work

Validate each formal Manifest by itself for schema well-formedness and consistency within its modeled boundary declarations. Validate each Contract and Solution independently as well.
AN-T-3975 covers cross-artifact checks.

## Acceptance

Validation reports malformed, internally inconsistent, missing, and unresolved Manifest declarations with source links; it does not compare a Manifest to a Contract or Solution.

## Findings

Validated 55 Active and 13 Draft Manifest revisions independently.
The report records 48 unresolved Manifest revisions, including
unmodeled declarations. Standalone validation also checked 48
Contracts and 48 Solutions. Each result identifies the source revision.
