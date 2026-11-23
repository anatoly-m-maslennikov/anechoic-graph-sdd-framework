---
atom_family: SPEC
atom_id: AN-S-3971
container:
  component: C00
tier: 1
context:
  lens: DES
state:
  status: archived
  version: 23
  updated_at: 2026-10-24 09:20:34 +0400
---
## Summary

Govern each scope by authority mode

# Govern each scope by authority mode

the anechoic Project **must** use the effective Authority Mode for the Project **and** **every** configured Scope Unit under CA-R-1430:

- Framework Instance Settings selects the Project mode **and** the default Scope Unit mode.
- a Scope Unit's explicit override comes **only** from its authoritative Project Structure declaration; an omitted override uses the effective Framework Instance setting.

mode selection **must not** weaken active-authority consistency.
