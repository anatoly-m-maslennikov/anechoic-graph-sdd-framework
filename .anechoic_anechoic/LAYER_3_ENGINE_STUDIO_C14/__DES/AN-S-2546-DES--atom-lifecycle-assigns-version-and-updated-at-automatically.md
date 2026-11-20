---
atom_family: SPEC
atom_id: AN-S-2546
structure:
  container:
    component: C14
  tier: 3
context:
  lens: DES
state:
  status: active
  version: 1
  updated_at: '2026-11-13T20:27:53.588756+00:00'
---
## Summary

Atom lifecycle assigns Version and Updated At automatically

## Claim

### Prose Claim

When a lifecycle operation creates a new Atom Version, the runtime assigns both Version and Updated At. Use Version 1 for a new Atom ID. For an existing ID, use one more than the highest Version across its Current, Draft and Archived carriers. Set Updated At to the creation time.

Promotion keeps the Draft’s Version and Updated At. The Draft Version may skip numbers and must be greater than the published predecessor’s Version.
