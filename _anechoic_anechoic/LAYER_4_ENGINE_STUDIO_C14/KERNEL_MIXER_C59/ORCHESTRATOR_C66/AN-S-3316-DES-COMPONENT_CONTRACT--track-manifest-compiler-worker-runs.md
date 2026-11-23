---
atom_family: SPEC
atom_id: AN-S-3316
container:
  component: C66
tier: 0
context:
  template: component_contract
  lens: DES
relations:
  ANSWERS:
  - AN-S-3315
state:
  status: "active"
  version: 2
  updated_at: '2026-11-22T22:21:58.378197+00:00'
---
## Summary

Track Manifest Compiler Worker runs

## Guarantee

For the admitted Project, start Model builds and Structure refreshes in
short-lived processes. Reap a process when it finishes or exceeds its
deadline. Report the active runs and the latest terminal run of each kind
through the declared Worker Run interface. Each record identifies the
run, its kind, the process if it started, and its status.

## References

AN-T-2944 and AN-S-3088.
