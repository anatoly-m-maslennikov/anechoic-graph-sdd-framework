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
  version: 24
  updated_at: 2026-11-02 00:18:22 +0400
---
## Summary

Serialize instance Authority Mode selections

## Claim scope

an explicit Authority Mode selection in the Framework Instance Settings TOML Carrier.

## Claim

an explicit Authority Mode selection **in** the Framework Instance Settings TOML Carrier **must** use `authority_modes.default` for the instance default **or** `authority_modes.project` for the Project override. explicit per-unit overrides **must** use **only** that unit's `authority_mode` **in** authoritative Project Structure; legacy per-unit Settings fields **must not** remain a second selectable source.
