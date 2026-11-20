---
atom_family: TKT
atom_id: AN-T-2794
structure:
  container:
    component: C00
  priority: 2
context:
  template: question
state:
  status: resolved
  version: 1
  updated_at: '2026-11-19T08:43:41.381554+00:00'
---
## Summary

Map legacy Open and Unresolved Concern statuses

## Concern

Should the mechanical migration treat legacy `open` and `unresolved` Concerns as Active Tickets?

## Details

CA-C-376 is Open. CA-C-353, CA-C-380 and CA-C-391 are Unresolved. All four are Current Project Problems. The existing decision maps `queued` to `active`. The Operator approved the mapping to Active for the four migrated copies.
Keep the original Concern statuses in the migration evidence.

## References

CA-P-3075, CA-C-746.
