---
atom_family: SPEC
atom_id: AN-S-3287
structure:
  container:
    component: C19
  tier: 1
context:
  template: component_contract
  lens: DES
state:
  status: "active"
  version: 1
  updated_at: "2026-11-21T18:48:44.527533+00:00"
---

## Summary

Run the Project Test Suite

## Guarantee

Given a Project root and an optional selection of source test Modules,
run the discovered or selected tests in fresh Python interpreters.
Report each Module's result and the suite totals on the output streams.

Return zero when the selected suite passes. Return a nonzero status when
selection, the required test environment, or a test Module fails. A
skipped required integration test fails the suite.

## References

AN-S-3055, AN-T-2944, and AN-T-2958.
