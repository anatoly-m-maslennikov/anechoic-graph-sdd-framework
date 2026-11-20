---
identity:
  atom_id: AN-S-2320
context:
  container:
    component: C27
  tier: 4
  lens: DevOps
state:
  status: active
  version: 15
  updated_at: 2026-11-09 15:54:30 +0400
---

## Summary

Serialize public remote effect proofs without secrets

## Scope

the remote proof of one public push.

## Claim

### Prose Claim

public remote effect evidence **must** retain the personal remote identity, branch direction, immutable commit identity, and repository-relative result/effect references without credentials, tokens, passwords, or arbitrary environment values.

## Details

An absent effect reference is not converted into a successful push claim.
