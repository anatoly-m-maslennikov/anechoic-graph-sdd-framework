---
atom_family: SPEC
atom_id: AN-S-1487
concern:
  subject: Rework risk prioritization
  path: Design Foundations/Reuse automation and maintenance
  relation: is_contained_by
container:
  component: C00
tier: 1
context:
  lens: SWD
  template: applicable_principle
state:
  status: "active"
  version: 6
  updated_at: "2026-11-27T13:00:59.972473+00:00"
relations:
  APPLIES:
  - AN-S-1434
  SERVES:
  - AN-S-1233
---

**P23**

## Summary

Prioritize problems by the rework they can cause

## Claim

### Prose Claim

Put the most effort into early checks and lasting fixes where a problem would force the most downstream work to be redone.

## Details

### Examples

Before a team builds several reports, it checks a data model error that would affect all of them. Fixing the model first avoids rebuilding the reports later.
