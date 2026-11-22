---
atom_family: TKT
atom_id: AN-T-2986
container:
  atom: AN-T-2944
priority: 2
context:
  template: task
  label: Task
state:
  status: "backlog"
  version: 1
  updated_at: "2026-11-22T16:48:46.912742+00:00"
---
## Summary

Review wrapper-only Package migrations

## Work

Review planned and existing wrappers that exist solely to route
imports through an entry Module. Retain compatibility entry points
where a documented caller relies on them.

Choose an owned interface, an exact declared bypass, or a Package
or Component move. Use recurring bypasses as evidence for a structural
move. Check dependency direction and layer order before moving an owner.

## Verification

Record each decision in the owning declarations and verify the result
in the Realization Graph. Keep declared bypasses visible. Verify the
affected behavior and check for new forbidden imports.

## References

AN-T-2946, AN-T-2958, and AN-S-3179.
