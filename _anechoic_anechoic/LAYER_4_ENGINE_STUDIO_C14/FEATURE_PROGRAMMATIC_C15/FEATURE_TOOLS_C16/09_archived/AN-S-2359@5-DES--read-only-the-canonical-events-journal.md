---
atom_family: SPEC
atom_id: AN-S-2359
container:
  component: C16
tier: 3
context:
  lens: DES
state:
  status: archived
  version: 5
  updated_at: 2026-10-24 00:51:05 +0400
---
## Summary

Read only the canonical Events Journal

# Summary

Read only the canonical Events Journal

## Scope

The FIND_AND_FETCH_JOURNAL_EVENTS Tool source boundary.

## Claim

FIND_AND_FETCH_JOURNAL_EVENTS **must** query only canonical Event carriers under the selected Project's `.anechoic_<project name>/_journal/` root.

## Details

Historical sealed Event references resolve only as immutable references. The source
is raw canonical JSON Event bytes: raw duplicate object keys are rejected before
parse, and no alternate log, derived projection, filename identity, or source
rewrite may substitute for canonical Events.
