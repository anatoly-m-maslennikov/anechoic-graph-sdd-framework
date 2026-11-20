---
identity:
  atom_id: AN-S-1195
context:
  container:
    component: C9
  tier: 3
  lens: DES
state:
  status: active
  version: 33
  updated_at: 2026-11-02 18:35:20 +0400
---
## Summary
Resolve skill routing precedence

## Claim

### Prose Claim

skill route resolution.


skill routes **must** resolve by explicit precedence: project-local ANECHOIC routes override framework routes, which override provider-global routes.
