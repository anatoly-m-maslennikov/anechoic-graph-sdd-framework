---
atom_family: TKT
atom_id: AN-T-3475
container:
  atom: AN-T-3468
priority: 2
context:
  template: task
  label: Task
relations:
  IS_REFERENCE:
  - AN-T-3473
  - AN-T-3474
  - AN-T-3471
state:
  status: done
  version: 1
  updated_at: '2026-11-23T23:07:47.000000+00:00'
---
## Summary

Check transitive effects and unresolved cases

## Work

Check known transitive effects against the pilot state and I/O guarantee using
the existing Code Analysis and Lean results. Prove that an unresolved call or
effect never passes the pilot acceptance path. Include one permitted case, one
forbidden case, and one unresolved case, with evidence for each.

## Acceptance

The checker records the transitive effects, maps them to the pilot state/I/O
guarantee, and shows that unresolved behavior cannot pass. The report contains
the permitted, forbidden, and unresolved cases and their evidence. Keep the
Adapter scope unchanged.
