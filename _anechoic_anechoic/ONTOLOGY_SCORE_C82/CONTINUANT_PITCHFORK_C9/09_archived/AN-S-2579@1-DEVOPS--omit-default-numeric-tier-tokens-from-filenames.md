---
atom_family: SPEC
atom_id: AN-S-2579
container:
  component: C9
tier: 3
context:
  lens: DevOps
state:
  status: archived
  version: 1
  updated_at: 2026-10-23 23:33:48 +0400
---
## Summary

Omit Default Numeric Tier Tokens from Filenames

# Summary

Omit Default Numeric Tier Tokens from Filenames

## Scope

Atom filenames whose registered grammar omits the default numeric Tier token.

## Claim

an Atom filename **may** omit the default Tier `3` token only where the registered filename grammar explicitly defines that omission. The Atom **must** still carry its numeric Tier internally under CA-R-2124; omission **must not** add, remove, or alter an Atom Property, infer a Content Role or Type restriction, or change the represented source Properties in a Projection or other non-Atom Artifact. A Project Goal's explicit Tier `-1` grammar is evaluated before any ordinary default omission.

## Details

