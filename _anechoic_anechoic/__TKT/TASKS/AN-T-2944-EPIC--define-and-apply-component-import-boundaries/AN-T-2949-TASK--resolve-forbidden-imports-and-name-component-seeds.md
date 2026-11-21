---
atom_family: TKT
atom_id: AN-T-2949
structure:
  container:
    atom: AN-T-2944
  priority: 2
context:
  template: task
state:
  status: "active"
  version: 2
  updated_at: "2026-11-21T19:07:45.166006+00:00"
---

## Summary

Resolve forbidden imports and name Component Seeds

## Work

Resolve forbidden cross-Component imports in descending Layer order.
Start with Framework Delivery (C27). Check each resolved import against
the Code Access of the owning Components and their exact entry points.
Keep Package-only findings outside this pass.

Preserve behavior while repairing imports. Begin the target architecture
refactor after verifying the cross-Component pass. Use Component Seed
as the name for Specified Package during that refactor.
