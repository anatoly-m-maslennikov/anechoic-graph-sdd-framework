---
atom_family: SPEC
atom_id: AN-S-2436
container:
  component: C19
tier: 3
context:
  lens: DES
state:
  status: archived
  version: 3
  updated_at: 2026-10-23 03:14:50 +0400
---
## Summary

Require immutable proof for public push

# Summary

Require immutable proof for public push

## Scope

one public `amm/dev` push effect.

## Claim

**the Operator** **must** retain an immutable commit identity and remote effect reference for every public push of the selected public source/material bindings.

## Details

The proof is evidence on the parent Action Run. Failure, partial effect, or absent proof does not permit PR advancement or inferred success.
