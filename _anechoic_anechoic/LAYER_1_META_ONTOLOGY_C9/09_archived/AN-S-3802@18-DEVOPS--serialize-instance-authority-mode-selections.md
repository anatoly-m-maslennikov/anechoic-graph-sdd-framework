---
atom_family: SPEC
atom_id: AN-S-3802
container:
  component: C9
tier: 6
context:
  lens: DevOps
state:
  status: archived
  version: 18
  updated_at: 2026-10-24 09:42:52 +0400
---
## Summary

Serialize instance Authority Mode selections

# Summary

Serialize instance Authority Mode selections

## Scope

an explicit Authority Mode selection in the Framework Instance Settings TOML Carrier.

## Claim

an explicit Authority Mode selection **in** the Framework Instance Settings TOML Carrier **must** use `authority_modes.default` for the instance default **or** `authority_modes.project` for the Project override. explicit per-unit overrides **must** use **only** that unit's `authority_mode` **in** authoritative Project Structure; legacy per-unit Settings fields **must not** remain a second selectable source.

## Details
