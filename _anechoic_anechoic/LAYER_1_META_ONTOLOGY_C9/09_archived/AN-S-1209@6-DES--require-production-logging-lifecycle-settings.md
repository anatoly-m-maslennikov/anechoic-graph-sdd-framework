---
atom_family: SPEC
atom_id: AN-S-1209
container:
  component: C9
tier: 3
context:
  lens: DES
state:
  status: archived
  version: 6
  updated_at: 2026-10-25 17:32:27 +0400
---
## Summary

Require production logging lifecycle settings

# Summary

Require production logging lifecycle settings

## Scope

production Logging Policies **and** their retention, access, sampling, rotation, maximum size, back-pressure, unavailable-sink, **and** disk-pressure conditions.

## Claim

a production Logging Policy **must** define retention, access, sampling, rotation, maximum size, back-pressure, unavailable-sink behavior, **and** disk-pressure behavior.

## Details

these settings define the policy’s retention **and** delivery controls.
