---
atom_family: SPEC
atom_id: AN-S-467
container:
  component: C9
tier: 7
context:
  lens: DevOps
state:
  status: active
  version: 29
  updated_at: '2026-11-20T11:29:16.622913+00:00'
---

## Summary

Serialize the Project Atom prefix

## Claim

The Project Manifest stores the exact Operator-selected `prefix` before the first native Atom is created. Validate the uppercase Prefix against the native Atom ID format. Reject an invalid value without trimming or changing its case.
