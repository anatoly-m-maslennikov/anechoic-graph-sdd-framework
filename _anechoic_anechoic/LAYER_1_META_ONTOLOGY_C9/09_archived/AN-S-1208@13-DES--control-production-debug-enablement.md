---
atom_family: SPEC
atom_id: AN-S-1208
container:
  component: C9
tier: 3
context:
  lens: DES
state:
  status: archived
  version: 13
  updated_at: 2026-11-02 00:18:22 +0400
---
## Summary

Control production DEBUG enablement

## Claim scope

logging Implementation for production DEBUG logging under Logging Policies.

## Claim

logging Implementation **must** keep production DEBUG logging disabled by default. temporary enablement **must** be scoped by component, subject, run, entity, **or** another bounded selector, have an automatic expiry, **and** preserve the same redaction rules as **every** other level.

## Details

the selector **and** expiry bound temporary production DEBUG use while preserving its required redaction treatment.
