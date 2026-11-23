---
atom_family: SPEC
atom_id: AN-S-1195
container:
  component: C9
tier: 3
context:
  lens: DES
state:
  status: archived
  version: 23
  updated_at: 2026-10-25 01:04:58 +0400
---
## Summary

Resolve skill routing precedence

# Summary
Resolve skill routing precedence

## Scope
skill route resolution.

## Claim

skill routes **must** resolve by explicit precedence: project-local ANECHOIC routes override framework routes, which override provider-global routes.

## Details
