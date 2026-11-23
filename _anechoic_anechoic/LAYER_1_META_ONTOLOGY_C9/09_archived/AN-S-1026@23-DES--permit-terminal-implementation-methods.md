---
atom_family: SPEC
atom_id: AN-S-1026
container:
  component: C9
tier: 3
context:
  lens: DES
state:
  status: archived
  version: 23
  updated_at: 2026-10-25 17:32:27 +0400
---
## Summary

Permit terminal Implementation Methods

# Summary

Permit terminal Implementation Methods

## Scope

terminal permission for an active Eng Policy after its local Eng Decisions are absorbed and archived.

## Claim

`eng_policy` **must** be registered as terminal-permitted, so an active Eng Policy Atom **may** remain childless in Atom topology **after** its local Eng Decision Atoms have been losslessly absorbed **and** archived.

## Details

This Atom-topology permission does not create a Scope Unit child or grant local Eng Policy ownership to a leaf; an actual declared child and every-child applicability remain required by CA-R-2119.
