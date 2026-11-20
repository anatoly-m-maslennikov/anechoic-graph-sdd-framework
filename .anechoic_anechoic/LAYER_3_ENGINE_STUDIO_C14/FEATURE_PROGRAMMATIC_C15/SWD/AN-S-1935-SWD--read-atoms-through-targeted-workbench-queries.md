---
identity:
  atom_id: AN-S-1935
context:
  container:
    component: C15
  tier: 5
  lens: SWD
state:
  status: active
  version: 7
  updated_at: '2026-11-12T12:32:34.877803+00:00'
---
## Summary

Read Atoms through targeted Workbench queries

## Claim

### Prose Claim

Use the selected Project’s `query_run` for Atom reads, including reads of Current, Draft, and Archived Atoms inside write operations. Select the exact carriers and retrieve derived relations through `query_run`. Filter rows in SQL, select only the columns needed, and use joins or CTEs when they avoid repeated queries. Reuse results across steps that need the same data.

When an operation needs exact source bytes, a single-target operation may read at most one Atom file directly. Batch Archive, batch Promote Draft, and Plan Status cascades may read at most one exact Atom file per target. Every direct read uses the Project-relative path and filename already selected through `query_run`. Reuse the bytes within the call without keeping a persistent copy.

## Details

Preserve the exact Atom ID spelling during selection. Its numeric part is one or more digits from 0 to 9, including leading zeros. For lifecycle selection, use the first valid native carrier that matches the requested Atom and, when supplied, its expected Version. Report a missing or stale selection explicitly. If the requested Archive is unloaded, report that separately. Workbench reports duplicate Current and Archived revisions through its audit. Verify the selected carrier’s expected state before a write and check the actual effects. Queries within an operation must see changes already made by that operation.
