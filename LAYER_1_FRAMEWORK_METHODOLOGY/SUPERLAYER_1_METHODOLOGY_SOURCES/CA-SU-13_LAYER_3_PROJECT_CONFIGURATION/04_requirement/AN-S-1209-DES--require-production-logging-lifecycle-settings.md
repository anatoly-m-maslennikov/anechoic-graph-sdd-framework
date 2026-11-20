---
atom_family: SPEC
atom_id: AN-S-1209
structure:
  container:
    component: C9
  tier: 3
context:
  lens: DES
state:
  status: active
  version: 14
  updated_at: 2026-11-02 19:44:26 +0400
---
## Summary

Require production logging lifecycle settings

## Claim

### Prose Claim


production Logging Policies **and** their retention, access, sampling, rotation, maximum size, back-pressure, unavailable-sink, **and** disk-pressure conditions.


a production Logging Policy **must** define retention, access, sampling, rotation, maximum size, back-pressure, unavailable-sink behavior, **and** disk-pressure behavior.

## Details

these settings define the policy’s retention **and** delivery controls.
