---
identity:
  atom_id: AN-S-466
context:
  container:
    component: C9
  tier: 7
  lens: DevOps
state:
  status: "active"
  version: 31
  updated_at: "2026-11-20T11:29:16.618830+00:00"
---

## Summary

Serialize Project initialization identity

## Claim

The Project Manifest stores the Operator-selected Project Name as `name` before the first native Atom is created. Preserve the selected spelling. Control-root selection checks the case-folded Name without changing the stored value.
