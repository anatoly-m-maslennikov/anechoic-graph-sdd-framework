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
  status: archived
  version: 1
  updated_at: "2026-11-27T16:16:01.404965+00:00"
---

## Summary

Keep Studio available when Project data has issues

## Claim

### Prose Claim

Keep Studio running and serve health and diagnostics when the Project’s Anechoic control directory is missing, unreadable, or contains invalid data. Keep operations on admitted data available. Return explicit errors for operations that require unavailable inputs.

During reads and indexing, treat a Project file that cannot be read,
parsed, or validated as a warning. Admit usable Atom data.

Report each warning with its cause and source path. Show Atom findings
in the Workbench Issues tables with the exact Atom reference when
available. Report missing or unusable Project inputs as Project-level
issues.

Apply write and lifecycle validation. Return an explicit error if a
requested operation fails validation.
