---
atom_family: SPEC
atom_id: AN-S-1488
concern:
  subject: Assessment of costly assumptions
  path: Design Foundations/Reuse automation and maintenance
  relation: is_contained_by
container:
  component: C00
tier: 2
context:
  lens: SWD
  template: applicable_principle
state:
  status: "active"
  version: 6
  updated_at: "2026-11-27T13:00:59.981594+00:00"
relations:
  CONTRIBUTES_TO:
  - AN-S-1487
---

**P24**

## Summary

Test costly assumptions before building on them

## Claim

### Prose Claim

Check assumptions that would force substantial rework if wrong.

## Details

### Examples

Before building a large import workflow, a team tests whether the source data contains stable identifiers. The test can reveal a costly mismatch before the team builds on that assumption.
