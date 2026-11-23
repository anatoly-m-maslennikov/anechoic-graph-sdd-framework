---
atom_family: SPEC
atom_id: AN-S-2399
container:
  component: C17
tier: 3
context:
  lens: DES
state:
  status: archived
  version: 3
  updated_at: 2026-10-23 01:47:30 +0400
---
## Summary

Read one complete TOML configuration

# Summary

Read one complete TOML configuration

## Scope

effect-free complete Read of one explicit Project Structure **or** Project Settings configuration through the shared TOML connector.

## Claim

the Configuration Read result **must** contain the complete authoritative TOML source **and** its complete parsed values for exactly one logical configuration **in** the bound Project, with exact observed source-state evidence **and** no mutation. Read is independently callable **without** Query, Modify **or** an enclosing Workflow.

an unpinned current Read **must not** require a pre-known source pin. a supplied pin **or** explicit historical view **must** match the exact available admitted source; missing history **or** stale evidence **must not** fall back **to** the latest source. the caller's context selects source authority **and** schema; the connector checks these bindings **without** choosing them. missing, ambiguous, denied, invalid **or** unreadable sources **must** return a structured failure, **not** a successful empty **or** partial document.

## Details

CA-D-631 fixes the representation **and** CA-O-218 binds Read on the same TOML connector as CA-O-204 Modify. no configuration, Carrier, history, Version, timestamp, lifecycle **or** runtime state is changed by Read. this contract does **not** admit a live route, a new backend **or** new history retention.
