---
atom_family: SPEC
atom_id: AN-S-4721
container:
  component: C14
tier: 1
context:
  template: POLICY
  lens: DES
state:
  status: active
  version: 1
  updated_at: '2026-11-23T13:57:04.062935+00:00'
---

## Summary

Keep Studio available when Project data has issues

## Claim

### Prose Claim

Keep Studio running and serve health and diagnostics when the Project’s Anechoic control directory is missing, unreadable, or contains invalid data. Keep operations on admitted data available. Return explicit errors for operations that require unavailable inputs.

Index usable Atom data. Report Atom findings in the Workbench Issues tables with the source path and exact Atom reference when available. Report missing or unusable Project inputs as Project-level issues.
