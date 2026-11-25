---
atom_family: SPEC
atom_id: AN-S-1611
container:
  component: C58
tier: 1
context:
  lens: DOM/MTD
state:
  status: "archived"
  version: 27
  updated_at: "2026-11-25T23:03:08.762419+00:00"
---
## Summary

Keep Evaluation implementation coverage explicit

## Claim

### Prose Claim


Coverage between QA Specs and their implementations.


QA Specs and implementations may have many-to-many coverage when the results are explicitly attributable.

- **`=1`** QA Spec may be realized by multiple distinct implementations.
- **`=1`** implementation **may** realize multiple QA Specs **only** **when** its result remains attributable **to** **every** covered Claim.

## Details

a shared implementation **must not** make its covered Claims **or** their result attribution implicit. this Claim governs coverage, **not** a new Carrier **or** a second implementation registry.
