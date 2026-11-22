---
atom_family: SPEC
atom_id: AN-S-347
container:
  component: C9
tier: 1
context:
  lens: DES
state:
  status: active
  version: 22
  updated_at: 2026-11-02 00:18:22 +0400
---
## Summary

Separate Projection derivation from Carrier materialization

## Claim

### Prose Claim


the derivation of a Projection and its Carrier materialization.


the governing derivation logic of a Projection **must** remain distinct from its Carrier materialization strategy. whether **and** how its result is represented **or** persisted **in** Carriers does **not**, by itself, define the transformation **or** content-preservation behavior of that derivation, its semantic Type, **or** its refresh behavior; those remain determined by their applicable governing Claims. describing a derivation as direct **or** content-preserving does **not** select a persistence strategy.
