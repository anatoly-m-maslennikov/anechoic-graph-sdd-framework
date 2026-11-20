---
atom_family: SPEC
atom_id: AN-S-2938
structure:
  container:
    component: C9
  tier: 3
context:
  lens: DES
state:
  status: draft
  version: 1
  updated_at: 2026-11-05 14:25:52 +0400
---
## Summary

Define recursive Property selection with `**`

## Claim

### Prose Claim

Within one bearer, `p.**` selects the distinct dependent Property identities recursively below Property `p` across all descendant depths. `p.**{::n}` counts that selected set across all descendant depths; it does not count values or Properties belonging to another bearer.
