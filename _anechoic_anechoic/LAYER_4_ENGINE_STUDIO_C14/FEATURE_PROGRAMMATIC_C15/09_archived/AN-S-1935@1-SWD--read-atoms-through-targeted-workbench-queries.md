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
  version: 1
  updated_at: '2026-11-11T22:37:20.213205+00:00'
---
## Summary

Read Atoms through targeted Workbench queries

## Claim

### Prose Claim

Read Atom data through the selected Project’s `query_run`. Filter rows in SQL and select only the columns needed by the caller. Use joins or CTEs to retrieve related rows together when that avoids repeated queries. Reuse the result across steps that need the same data.

## Details

An exact Atom lookup must report missing, ambiguous or stale data. Before a write, check the selected carrier and its expected state. Steps in the same operation must see the Atom changes already made by that operation.
