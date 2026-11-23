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
  version: 2
  updated_at: '2026-11-11T22:41:45.412226+00:00'
---
## Summary

Read Atoms through targeted Workbench queries

## Claim

### Prose Claim

Use the selected Project’s `query_run` for every Atom read, without exception. This covers Current, Draft, and Archived Atoms and every Atom read inside a lifecycle tool or any other write operation. Filter rows in SQL and select only the columns the caller needs. Use joins or CTEs when they avoid repeated queries. Reuse results across steps that need the same data.

## Details

For an exact lookup, report missing, ambiguous, or stale results. Use query results to verify the expected Atom state for writes. A query in the same operation must see Atom changes already made by that operation.
