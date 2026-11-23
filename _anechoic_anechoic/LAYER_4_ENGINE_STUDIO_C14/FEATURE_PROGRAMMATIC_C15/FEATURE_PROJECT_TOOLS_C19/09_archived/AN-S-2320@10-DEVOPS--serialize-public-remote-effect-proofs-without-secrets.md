---
atom_family: SPEC
atom_id: AN-S-2320
container:
  component: C19
tier: 4
context:
  lens: DevOps
state:
  status: archived
  version: 10
  updated_at: 2026-10-24 23:44:24 +0400
---
## Summary

Serialize public remote effect proofs without secrets

# Summary

Serialize public remote effect proofs without secrets

## Scope

the remote proof of one public push.

## Claim

public remote effect evidence **must** retain the personal remote identity, branch direction, immutable commit identity, and repository-relative result/effect references without credentials, tokens, passwords, or arbitrary environment values.

## Details

An absent effect reference is not converted into a successful push claim.
