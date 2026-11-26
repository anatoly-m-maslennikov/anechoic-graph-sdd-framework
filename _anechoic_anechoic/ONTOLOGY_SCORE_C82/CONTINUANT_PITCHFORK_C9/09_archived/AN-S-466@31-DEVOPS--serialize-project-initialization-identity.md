---
atom_family: SPEC
atom_id: AN-S-466
container:
  component: C9
tier: 7
context:
  lens: DevOps
state:
  status: "archived"
  version: 31
  updated_at: "2026-11-25T23:12:30.703126+00:00"
---

## Summary

Serialize Project initialization identity

## Claim

The Project Manifest stores the Operator-selected Project Name as `name` before the first native Atom is created. Preserve the selected spelling. Control-root selection checks the case-folded Name without changing the stored value.
