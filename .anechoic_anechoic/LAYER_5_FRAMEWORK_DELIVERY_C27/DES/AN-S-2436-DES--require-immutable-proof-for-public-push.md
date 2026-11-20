---
identity:
  atom_id: AN-S-2436
context:
  container:
    component: C27
  tier: 3
  lens: DES
state:
  status: active
  version: 15
  updated_at: 2026-11-09 15:54:30 +0400
---

## Summary

Require immutable proof for public push

## Scope

one public `amm/dev` push effect.

## Claim

### Prose Claim

**the Operator** **must** retain an immutable commit identity and remote effect reference for every public push of the selected public source/material bindings.

## Details

The proof is evidence on the parent Action Run. Failure, partial effect, or absent proof does not permit PR advancement or inferred success.
