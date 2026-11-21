---
atom_family: SPEC
atom_id: AN-S-2551
container:
  component: C43
tier: 3
context:
  lens: DES
state:
  status: draft
  version: 11
  updated_at: '2026-11-14T07:53:12.919343+00:00'
---
## Summary

Provide native SQL query capability over query projection

## Claim

### Prose Claim

Run and Check synchronously against the synchronized Atom Projection.
Each accepts one complete native read-only query.

## Details

- Cursor position is editor metadata. Reject multiple statements. Invalid
  SQL returns a query error distinct from a source-file failure.
- Queries preserve source files and source-derived Projection data.
- `query_schema` exposes actual tables and columns, including declared Content
  and optional distinct non-null Header Status values for escaped completion.
- Schema reads execute no SQL and leave the saved Journal untouched.
- Unsaved Run, Check, and Page have no saved-item effects.
