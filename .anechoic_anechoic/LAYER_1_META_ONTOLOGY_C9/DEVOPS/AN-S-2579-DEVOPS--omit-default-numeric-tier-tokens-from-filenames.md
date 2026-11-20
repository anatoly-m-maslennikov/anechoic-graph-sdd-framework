---
identity:
  atom_id: AN-S-2579
context:
  container:
    component: C9
  tier: 4
  lens: DevOps
state:
  status: active
  version: 13
  updated_at: 2026-11-02 00:18:22 +0400
---
## Summary

Omit Default Numeric Tier Tokens from Filenames

## Claim

### Prose Claim


Atom filenames whose registered grammar omits the default numeric Tier token.


an Atom filename **may** omit the default Tier `3` token only where the registered filename grammar explicitly defines that omission. The Atom **must** still carry its numeric Tier internally under CA-R-2706; omission **must not** add, remove, or alter an Atom Property, infer a Content Role or Type restriction, or change the represented source Properties in a Projection or other non-Atom Artifact. A Project Goal's explicit Tier `-1` grammar is evaluated before any ordinary default omission.
