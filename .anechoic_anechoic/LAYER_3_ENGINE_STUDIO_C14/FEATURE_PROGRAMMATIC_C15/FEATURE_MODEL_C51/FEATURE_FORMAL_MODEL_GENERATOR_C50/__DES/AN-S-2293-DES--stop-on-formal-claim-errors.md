---
atom_family: SPEC
atom_id: AN-S-2293
structure:
  container:
    component: C50
  tier: 3
context:
  lens: DES
state:
  status: active
  version: 1
  updated_at: '2026-11-13T10:43:02.276377+00:00'
---
## Summary

Stop on Formal Claim errors

## Claim

### Prose Claim

When a Formal Claim fails, write the error to stderr and stop the affected build or runtime operation. Do not retry or repair the Claim.
