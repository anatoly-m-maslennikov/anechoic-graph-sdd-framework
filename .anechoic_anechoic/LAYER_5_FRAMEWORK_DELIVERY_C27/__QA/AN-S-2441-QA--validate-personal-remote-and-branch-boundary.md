---
atom_family: SPEC
atom_id: AN-S-2441
structure:
  container:
    component: C27
  tier: 5
context:
  lens: QA
state:
  status: active
  version: 12
  updated_at: 2026-11-09 15:54:30 +0400
---

## Summary

Validate personal remote and branch boundary

## Scope

the remote and branch fields of one public-release request.

## Claim

### Prose Claim

**the Operator** **must** verify that only an explicit personal remote with `amm/dev` head and `main` base is admitted, while missing remote identity, another scope, or any branch change is refused before effects.

## Details

The case verifies configuration boundaries, not remote credentials or GitHub access.
