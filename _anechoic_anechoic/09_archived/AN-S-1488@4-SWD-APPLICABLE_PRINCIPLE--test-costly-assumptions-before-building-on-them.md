---
atom_family: SPEC
atom_id: AN-S-1488
container:
  component: C00
tier: 2
context:
  lens: SWD
  template: applicable_principle
state:
  status: "archived"
  version: 4
  updated_at: "2026-11-27T11:25:48.078391+00:00"
relations:
  CONTRIBUTES_TO:
  - AN-S-1487
---

## Summary

Test costly assumptions before building on them

## Claim

### Prose Claim

Check assumptions that would force substantial rework if wrong.

## Details

### Examples

Before building a large import workflow, a team tests whether the source data contains stable identifiers. The test can reveal a costly mismatch before the team builds on that assumption.
