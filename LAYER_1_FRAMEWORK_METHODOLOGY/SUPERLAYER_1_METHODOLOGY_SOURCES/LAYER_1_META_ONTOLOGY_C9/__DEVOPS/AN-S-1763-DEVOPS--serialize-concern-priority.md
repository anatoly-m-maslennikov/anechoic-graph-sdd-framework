---
atom_family: SPEC
atom_id: AN-S-1763
structure:
  container:
    component: C9
  tier: 3
context:
  lens: DevOps
state:
  status: active
  version: 23
  updated_at: 2026-11-02 00:18:22 +0400
---
## Summary

Serialize Concern Priority

## Claim

### Prose Claim


Concern Atom Carriers and non-Concern Content Role Atom Carriers.


a Concern Atom Carrier **must** serialize **`=1`** selected Priority as `priority` with the lowercase value `high`, `medium`, **or** `low`. **every** non-Concern Content Role Atom Carrier **must** omit `priority`; virtual `highest` **must not** be stored.
