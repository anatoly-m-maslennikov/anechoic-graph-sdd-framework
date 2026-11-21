---
atom_family: SPEC
atom_id: AN-S-3219
container:
  component: C00
tier: 3
context:
  lens: DES
state:
  status: archived
  version: 33
  updated_at: 2026-11-02 18:35:20 +0400
---
## Summary
Resolve skill routing precedence

## Claim scope
skill route resolution.

## Claim

skill routes **must** resolve by explicit precedence: project-local ANECHOIC routes override framework routes, which override provider-global routes.
