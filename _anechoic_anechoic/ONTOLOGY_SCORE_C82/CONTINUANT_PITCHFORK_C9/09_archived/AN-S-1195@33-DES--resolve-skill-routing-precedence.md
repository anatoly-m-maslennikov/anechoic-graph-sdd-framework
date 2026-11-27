---
atom_family: SPEC
atom_id: AN-S-1195
container:
  component: C9
tier: 3
context:
  lens: DES
state:
  status: "archived"
  version: 33
  updated_at: "2026-11-26T10:14:08.975256+00:00"
---
## Summary
Resolve skill routing precedence

## Claim

### Prose Claim

skill route resolution.


skill routes **must** resolve by explicit precedence: project-local ANECHOIC routes override framework routes, which override provider-global routes.
