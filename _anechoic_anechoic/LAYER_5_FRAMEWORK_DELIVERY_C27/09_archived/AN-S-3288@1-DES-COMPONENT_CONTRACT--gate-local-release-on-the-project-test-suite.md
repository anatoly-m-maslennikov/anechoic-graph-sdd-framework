---
atom_family: SPEC
atom_id: AN-S-3288
container:
  component: C27
tier: 1
context:
  template: component_contract
  lens: DES
state:
  status: archived
  version: 1
  updated_at: '2026-11-21T19:38:49.554487+00:00'
---

## Summary

Gate Local Release on the Project Test Suite

## Guarantee

For an admitted Local Release request, run the Project Test Suite before
replacing the release product or the installed runtime.

If the suite fails, report the tests step and make its output available.
Leave the existing product and installation in place.

## References

AN-S-1976, AN-S-3287, AN-T-2944, and AN-T-2958.
