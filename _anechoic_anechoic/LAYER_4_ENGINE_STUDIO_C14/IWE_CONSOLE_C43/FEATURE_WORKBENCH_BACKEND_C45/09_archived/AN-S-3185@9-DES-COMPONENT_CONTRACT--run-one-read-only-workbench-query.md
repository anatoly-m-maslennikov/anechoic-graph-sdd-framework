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
  version: 9
  updated_at: "2026-11-22T09:10:11.337382+00:00"
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

## Tool API

Publish the enabled Tool names, descriptions, and schemas for an admitted
Project. Use the same registry to validate and dispatch named calls.
Return the Tool result or a failure for a stale registry, disabled Tool,
or invalid request.

## Process boundary

Resolve the requested Project and return its Manifest pin and verified
host binding without opening DuckDB. Return its normalized Tool blacklist and
release workflow enablement.

Serve one admitted Project per Backend process over a private Unix
socket. Check the Project Manifest revision and instance identity before
readiness. Validate named Workbench operations in the Backend and call
the Project's Kernel to execute queries and publish lifecycle updates.
When release workflows are enabled, revalidate the Project Manifest pin and
return the host command for the declared local or public Release entrypoint.

Use the Project Manifest's storage settings first, then the host
defaults. The caller owns the process lifetime and closes it when the
Project leaves the pool or the caller exits.

## References

AN-S-1456, AN-S-2566, AN-S-3059, and AN-T-2947.
