---
atom_family: SPEC
atom_id: AN-S-452
container:
  component: C9
tier: 1
context:
  lens: DevOps
state:
  status: archived
  version: 25
  updated_at: 2026-10-27 19:59:23 +0400
---
## Summary

Separate Persistent Authority from Runtime State

# Summary

Separate Persistent Authority from Runtime State

## Scope

persistent Carriers holding canonical authority or retained history, in relation to runtime cleanup.

## Claim

runtime cleanup **must not** remove persistent Carriers holding canonical authority or retained history.

## Details

Delivery placement and retention rules must keep that content outside the cleanup target set. This protection does not require a Carrier.Ownership Class or Carrier.Storage Boundary property, and it does not classify a Carrier as disposable merely because a runtime uses it.

