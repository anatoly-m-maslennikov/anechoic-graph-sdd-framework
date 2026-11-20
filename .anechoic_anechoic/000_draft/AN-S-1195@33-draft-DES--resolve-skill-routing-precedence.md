---
identity:
  atom_id: AN-S-1195
context:
  container:
    component: C00
  tier: 3
  lens: DES
state:
  status: draft
  version: 33
  updated_at: 2026-11-02 18:35:20 +0400
---
## Summary
Resolve skill routing precedence

## Claim scope
skill route resolution.

## Claim

skill routes **must** resolve by explicit precedence: project-local ANECHOIC routes override framework routes, which override provider-global routes.
