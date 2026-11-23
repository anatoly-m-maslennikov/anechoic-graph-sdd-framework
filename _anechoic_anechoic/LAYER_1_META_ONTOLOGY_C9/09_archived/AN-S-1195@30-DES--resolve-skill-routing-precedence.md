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
  version: 30
  updated_at: 2026-10-29 14:16:33 +0400
---
## Summary
Resolve skill routing precedence

## Claim scope
skill route resolution.

## Claim

skill routes **must** resolve by explicit precedence: project-local ANECHOIC routes override framework routes, which override provider-global routes.
