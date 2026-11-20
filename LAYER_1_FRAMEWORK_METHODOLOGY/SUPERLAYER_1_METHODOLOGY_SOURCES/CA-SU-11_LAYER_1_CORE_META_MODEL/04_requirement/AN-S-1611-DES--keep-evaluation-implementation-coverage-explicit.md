---
atom_family: SPEC
atom_id: AN-S-1611
structure:
  container:
    component: C9
  tier: 1
context:
  lens: DES
state:
  status: active
  version: 26
  updated_at: 2026-11-10 14:38:45 +0400
---
## Summary

Keep Evaluation implementation coverage explicit

## Claim

### Prose Claim


coverage between Evaluation Atoms and their implementation realizations.


coverage between Evaluation Atoms **and** their realizations **may** be many-to-many **only** with explicit attribution:

- **`=1`** Evaluation Atom **may** be realized by multiple distinct implementations.
- **`=1`** implementation **may** realize multiple Evaluation Atoms **only** **when** its result remains attributable **to** **every** covered Claim.

## Details

a shared implementation **must not** make its covered Claims **or** their result attribution implicit. this Claim governs coverage, **not** a new Carrier **or** a second implementation registry.
