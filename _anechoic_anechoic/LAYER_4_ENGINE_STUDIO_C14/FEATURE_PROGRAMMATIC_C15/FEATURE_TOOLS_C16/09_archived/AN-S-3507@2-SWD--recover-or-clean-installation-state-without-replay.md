---
atom_family: SPEC
atom_id: AN-S-3507
container:
  component: C16
tier: 3
context:
  lens: SWD
state:
  status: archived
  version: 2
  updated_at: 2026-10-14 20:53:35 +0400
---
## Summary

Recover or clean installation state without replay

# Summary

Recover or clean installation state without replay

## Scope

the inspection-only recovery and later separately approved cleanup procedure.

## Claim

the INSTALL_TOOLS facade **must** recover by reopening exact retained evidence or clean by later exact approval, and **must not** replay uncertain effects, bypass a lock or delete unapproved paths.

## Details

1. Reopen selector, context, package, generation and Journal evidence under the target lock; report actual blocked, partial or recording-pending state.
2. Recover only missing recording whose immutable effect inputs and terminal ownership agree; do not rebuild, reselect or start a new run.
3. For cleanup, reopen CA-D-609's exact approval, inventory and quiescence result, then remove only listed paths and record result. Any disagreement refuses.
