---
atom_family: SPEC
atom_id: AN-S-475
container:
  component: C9
tier: 4
context:
  lens: DevOps
state:
  status: archived
  version: 15
  updated_at: 2026-10-24 09:42:52 +0400
---
## Summary

Reuse framework parameter fields in Default Settings

# Summary

Reuse framework parameter fields in Default Settings

## Scope

parameter values in the Default Settings TOML Carrier.

## Claim

**every** parameter value **in** the Default Settings TOML Carrier **must** use the same registered section, field path, value type, **and** allowed domain as the corresponding explicit Framework Instance Settings parameter, **without** introducing a separate defaults-field schema.

## Details
