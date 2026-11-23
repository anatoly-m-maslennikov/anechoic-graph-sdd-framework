---
atom_family: SPEC
atom_id: AN-S-3304
container:
  component: C16
tier: 0
context:
  template: component_contract
  lens: DES
relations:
  ANSWERS:
  - AN-S-3056
state:
  status: "active"
  version: 2
  updated_at: '2026-11-22T22:21:56.598022+00:00'
---
## Summary

Apply one admitted native lifecycle operation

## Guarantee

For the selected Project, dispatch one supported Atom lifecycle operation
against the admitted carrier capture. For a change to an existing Atom,
require its exact expected revision. Return the outcome and observed file
effects. Reject an invalid or stale target before writing.

## References

AN-S-3056 and AN-T-2947.
