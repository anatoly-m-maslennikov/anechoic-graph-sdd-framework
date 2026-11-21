---
atom_family: SPEC
atom_id: AN-S-2768
structure:
  container:
    component: C9
  tier: 1
context:
  lens: DevOps
state:
  status: draft
  version: 30
  updated_at: 2026-11-05 06:15:15 +0400
---
## Summary

Prohibit Persisting Derived Containment

## Claim

### Prose Claim

The `IS_CONTAINED_BY` fact declared through an Atom’s `Header.Container` and the `CONTAINS` view derived from it must not be persisted as additional independent Relation declarations merely because Carrier placement is read back.

## Details

Carrier placement follows the declared Container. Its readback identifies the same containment fact; it does not establish another logical parent. An independently admitted direct `IS_CONTAINED_BY` fact remains governed by its own source. `CONTAINS` is the derived inverse and is not independently authored. Do not maintain two independent sources for the same fact.
