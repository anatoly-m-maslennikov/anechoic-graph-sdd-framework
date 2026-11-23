---
atom_family: SPEC
atom_id: AN-S-2441
container:
  component: C19
tier: 3
context:
  lens: QA
state:
  status: archived
  version: 1
  updated_at: 2026-10-10 19:05:35 +0400
---
## Summary

Validate personal remote and branch boundary

# Summary

Validate personal remote and branch boundary

## Scope

the remote and branch fields of one public-release request.

## Claim

**the Operator** **must** verify that only an explicit personal remote with `amm/dev` head and `main` base is admitted, while missing remote identity, another scope, or any branch change is refused before effects.

## Details

The case verifies configuration boundaries, not remote credentials or GitHub access.
