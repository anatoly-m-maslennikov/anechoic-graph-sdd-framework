---
atom_family: SPEC
atom_id: AN-S-1611
container:
  component: C58
tier: 1
context:
  lens: DOM/MTD
state:
  status: "active"
  version: 28
  updated_at: "2026-11-25T23:03:08.772670+00:00"
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

a shared implementation **must not** make its covered Claims **or** their result attribution implicit. State the corrected failure class in a recurrence check and use an applicable test, evaluation, or monitor. Retain actual business check outcomes through the governed recording path. this Claim governs coverage, **not** a new Carrier **or** a second implementation registry.
