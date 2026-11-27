---
atom_family: TKT
atom_id: AN-T-3473
container:
  atom: AN-T-3468
priority: 2
context:
  template: task
  label: Task
state:
  status: done
  version: 1
  updated_at: '2026-11-26T16:39:58.733781+00:00'
---
## Summary

Resolve runtime dependency calls

## Work

For `frontmatter_bounds` and `source_body`, resolve every runtime dependency
call to its exact callable, parameter binding, runtime version, and source
line. Demonstrate the Python distinction between the old `re.search` call,
where the third argument binds `flags`, and a compiled `Pattern.search` call,
where the corresponding argument binds `pos`. Keep unknown calls explicitly
unresolved.

## Acceptance

The report identifies the exact callable, binding, runtime version, and source
line for each resolved call. It includes both binding demonstrations and lists
unknown calls as unresolved without inference.
