---
atom_family: SPEC
atom_id: AN-S-2377
container:
  component: C16
tier: 3
context:
  lens: SWD
state:
  status: archived
  version: 3
  updated_at: 2026-10-23 01:47:30 +0400
---
## Summary

Select and page Event query results

# Summary

Select and page Event query results

## Scope

Result construction.

## Claim

To construct results, the Tool **must** order snapshot matches deterministically, apply the bounded page, and expose IDs, selected fields, or full Events only in the requested mode with truthful coverage metadata.

## Details

The next-page token remains bound to the source snapshot, source/prefix hashes,
result selection, and configured limits. Before any continuation it revalidates
captured members and rejects changed, deleted, unreadable, or truncated captured
data, while allowing append strictly after the sealed prefix.
