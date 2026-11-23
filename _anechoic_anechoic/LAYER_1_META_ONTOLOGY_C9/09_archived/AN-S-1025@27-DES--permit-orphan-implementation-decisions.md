---
atom_family: SPEC
atom_id: AN-S-1025
container:
  component: C9
tier: 3
context:
  lens: DES
state:
  status: archived
  version: 27
  updated_at: 2026-11-02 00:18:22 +0400
---
## Summary

Permit orphan Implementation Decisions

## Claim scope

orphan permission for an active Eng Decision in strict authority mode.

## Claim

`eng_decision` **must** be registered as orphan-permitted, so an active Eng Decision **may** have no parent Eng Policy even **in** strict authority mode.

## Details

This Atom-topology permission does not create a local Policy owner at a leaf or justify artificial children; local Eng Policy ownership and child applicability remain governed by CA-R-2119@8 and CA-R-2120@8.
