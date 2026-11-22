---
atom_family: SPEC
atom_id: AN-S-3185
container:
  component: C45
tier: 1
context:
  template: component_contract
  lens: DES
state:
  status: "archived"
  version: 3
  updated_at: "2026-11-22T07:19:41.372065+00:00"
---

## Summary

Run one read-only Workbench query

## Guarantee

Given a complete SQL string and valid result options, execute one read-only
query against the selected Project's Workbench data. Treat the optional
cursor position as editor metadata.

Return result metadata with an inline page or a result file according to
the requested delivery mode and result format. Omit the SQL text from
the result. Reject invalid inputs and report query execution failures.

## Process boundary

Serve one admitted Project per Backend process over a private Unix
socket. Check the Project Manifest revision and instance identity before
readiness. Use the same Workbench owner for queries and updates after a
lifecycle operation.

Use the Project Manifest's storage settings first, then the host
defaults. The caller owns the process lifetime and closes it when the
Project leaves the pool or the caller exits.

## References

AN-S-1456, AN-S-2566, AN-S-3059, and AN-T-2947.
