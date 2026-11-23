---
atom_family: SPEC
atom_id: AN-S-2376
container:
  component: C16
tier: 4
context:
  lens: SWD
state:
  status: archived
  version: 6
  updated_at: 2026-10-24 11:58:20 +0400
---
## Summary

Evaluate shared query filters against Event selectors

# Summary

Evaluate shared query filters against Event selectors

## Scope

Journal selector binding to QUERY_FILTER.

## Claim

To evaluate an Event filter, the Tool **must** resolve Event selectors then apply CA-R-1850's shared QUERY_FILTER without altering its grammar or value semantics.

## Details

An unknown or ambiguous Event selector, or any shared-filter rejection, returns
the exact invalid-filter diagnostic and no partial match result.
