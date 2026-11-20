---
identity:
  atom_id: AN-S-452
context:
  container:
    component: C9
  tier: 1
  lens: DevOps
state:
  status: active
  version: 29
  updated_at: 2026-11-02 00:18:22 +0400
---
## Summary

Separate Persistent Authority from Runtime State

## Claim

### Prose Claim


persistent Carriers holding canonical authority or retained history, in relation to runtime cleanup.


runtime cleanup **must not** remove persistent Carriers holding canonical authority or retained history.

## Details

Delivery placement and retention rules must keep that content outside the cleanup target set. This protection does not require a Carrier.Ownership Class or Carrier.Storage Boundary property, and it does not classify a Carrier as disposable merely because a runtime uses it.
