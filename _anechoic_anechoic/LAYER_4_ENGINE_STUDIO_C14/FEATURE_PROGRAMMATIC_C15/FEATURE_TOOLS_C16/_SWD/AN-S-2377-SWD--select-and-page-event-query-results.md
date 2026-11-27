---
atom_family: SPEC
atom_id: AN-S-2377
container:
  component: C16
tier: 4
context:
  lens: SWD
state:
  status: active
  version: 12
  updated_at: "2026-11-27T16:29:34.309627+00:00"
---
## Summary

Select and page Event query results

## Scope

Result construction.

## Claim

### Prose Claim

To construct results, the Tool **must** order snapshot matches deterministically, apply the bounded page, and expose IDs, selected fields, or full Events only in the requested mode with truthful coverage metadata.

## Details

Bind the page token to the sealed source, result selection, and limits.
Apply AN-S-2364 to snapshot revalidation.
