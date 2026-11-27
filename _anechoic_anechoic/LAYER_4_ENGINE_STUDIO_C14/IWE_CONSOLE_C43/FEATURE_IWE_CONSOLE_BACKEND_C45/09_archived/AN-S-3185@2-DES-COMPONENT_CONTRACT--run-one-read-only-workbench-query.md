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
  version: 2
  updated_at: "2026-11-22T07:04:58.138931+00:00"
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

For the single-Project runtime, serve the declared Workbench API over a
private Unix socket. Admit one Project Manifest and instance identity
before readiness. Use one Workbench owner for queries and for projection
updates after lifecycle operations. Close the owner when the caller ends.

## References

AN-S-1456, AN-S-2566, AN-S-3059, and AN-T-2947.
