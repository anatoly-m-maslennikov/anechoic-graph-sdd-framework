---
atom_family: SPEC
atom_id: AN-S-1683
container:
  component: C9
tier: 1
context:
  lens: DES
state:
  status: archived
  version: 9
  updated_at: 2026-10-29 07:17:20 +0400
---
## Summary

Assign Project Goal Tier Minus One

# Summary

Assign Project Goal Tier Minus One

## Scope

Project Goal Atoms.

## Claim

Every Requirement Atom of Type Project Goal **must** target the Project, be owned by its Operator Actor instead of a Local Scope Unit, and carry exactly one numeric Tier `-1`. Tier `-1` is explicit, is not omitted, and is outside the ordinary nonnegative Tier range. This Rule does not impose an arbitrary Type-to-Tier restriction beyond verified Project Goal identity and ownership.

## Details

The Project Goal retains its Operator Actor owner. CA-D-637 uses its Target Project only as the derived ordering context; ordinary Goal ownership and Scope ordering are unchanged.
