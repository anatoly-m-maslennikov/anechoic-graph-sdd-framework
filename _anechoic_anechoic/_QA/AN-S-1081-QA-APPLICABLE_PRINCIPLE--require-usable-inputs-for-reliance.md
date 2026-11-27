---
atom_family: SPEC
atom_id: AN-S-1081
concern:
  subject: Input validity for reliance
  path: Design Foundations/Delegation and control
  relation: is_contained_by
container:
  component: C00
tier: 2
context:
  lens: QA
  template: applicable_principle
state:
  status: "active"
  version: 31
  updated_at: "2026-11-27T13:00:59.755344+00:00"
relations:
  CONTRIBUTES_TO:
  - AN-S-1458
---
**P1**

## Summary
Require usable inputs for reliance

## Claim

### Prose Claim


a governed conclusion **may** be treated as reliable for an affected use **only** **when** **every** required input is present, known, consistent, **and** valid.

## Details

### Examples

Before a release, an Operator checks that a test report matches the exact release image and covers all required suites. The Operator can then rely on it for the release review.
