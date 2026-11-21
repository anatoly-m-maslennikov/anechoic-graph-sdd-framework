---
atom_family: TKT
atom_id: AN-T-2763
container:
  atom: AN-T-2757
priority: 2
context:
  template: task
state:
  status: done
  version: 1
  updated_at: '2026-11-18T21:56:49.875593+00:00'
---
## Summary

Define package exports and import checks

## Work

Test
   Internal defaults for all Package categories, Public and Internal
   allowlists, and caller rules inherited by nested ordinary Packages and
   child Components. Test `__<visibility>.<extension>` with normal Python
   imports. Check a behavior Contract with no export list and explicit
   nonempty and empty lists. Accept direct import of a named Unit and
   reject importing its whole Module when only the Unit is exported.

## References

CA-P-3074.
