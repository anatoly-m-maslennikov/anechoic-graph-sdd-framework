---
atom_family: SPEC
atom_id: AN-S-1935
container:
  component: C15
tier: 5
context:
  lens: SWD
state:
  status: archived
  version: 5
  updated_at: '2026-11-12T01:53:36.588022+00:00'
---
## Summary

Read Atoms through targeted Workbench queries

## Claim

### Prose Claim

Use the selected Project’s `query_run` for Atom reads. To speed up a Workflow, at most one direct Atom read is allowed per run. That read opens exactly one Atom file by its already known Project-relative path and filename. All other Atom reads use `query_run`, including reads of Current, Draft, and Archived Atoms and reads inside write operations. Retrieve derived relations through `query_run`.

Filter rows in SQL and select only the columns the caller needs. Use joins or CTEs when they avoid repeated queries. Reuse results across steps that need the same data.

## Details

For lifecycle selection, use the first valid native carrier that matches the requested Atom and, when supplied, its expected Version. Report a missing or stale selection explicitly. If the requested Archive is unloaded, report that separately. Workbench reports duplicate Current and Archived revisions through its audit. Verify the selected carrier’s expected state before a write. Queries within an operation must see changes already made by that operation.
