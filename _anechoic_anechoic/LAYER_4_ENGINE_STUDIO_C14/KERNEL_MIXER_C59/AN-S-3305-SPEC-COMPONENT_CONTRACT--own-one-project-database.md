---
atom_family: SPEC
atom_id: AN-S-3305
container:
  component: C59
tier: 0
context:
  template: component_contract
  lens: SPEC
relations:
  ANSWERS:
  - AN-S-3047
state:
  status: "active"
  version: 2
  updated_at: '2026-11-22T22:21:57.994911+00:00'
---
## Summary

Own one Project database

## Guarantee

Admit one Project instance and its Manifest revision before opening
the Workbench database. Keep the connection, projection transactions,
and result snapshots in the Kernel process.

Execute the admitted database operations for that Project over the
declared private API. Reject calls for a different instance. Preserve
committed projection and result state when an operation fails.

## References

AN-S-3047, AN-S-1363, and AN-T-2947.
