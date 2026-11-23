---
atom_family: SPEC
atom_id: AN-S-3501
container:
  component: C16
tier: 3
context:
  lens: DES
state:
  status: archived
  version: 2
  updated_at: 2026-10-14 20:53:35 +0400
---
## Summary

Block migration when owned-process quiescence is unsafe

# Summary

Block migration when owned-process quiescence is unsafe

## Scope

the safe shutdown precondition for an owned legacy state switch.

## Claim

the INSTALL_TOOLS facade **must** quiesce **only** a process proved owned by its legacy subtree and generation/command evidence, and **must** block migration when that proof or shutdown result is unsafe.

## Details

Unknown, external, stale, ambiguous or non-responsive processes are never signaled, killed or replaced. Quiescence evidence records the request, response and deadline and is rechecked before copy/switch. A block preserves old state and history without selector mutation.
