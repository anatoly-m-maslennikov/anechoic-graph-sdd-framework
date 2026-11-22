---
atom_family: SPEC
atom_id: AN-S-3339
container:
  component: C68
tier: 1
context:
  template: component_contract
  lens: DES
state:
  status: "archived"
  version: 1
  updated_at: "2026-11-22T11:57:56.800533+00:00"
---
## Summary

Run a pinned Beta snapshot Worker

## Guarantee

Accept one snapshot build for the selected Project at a time. Launch the
Worker with the supplied Project binding and return its result or a
failure. Report the active build and the latest Worker outcome.

## References

AN-S-3337 and AN-T-2958.
