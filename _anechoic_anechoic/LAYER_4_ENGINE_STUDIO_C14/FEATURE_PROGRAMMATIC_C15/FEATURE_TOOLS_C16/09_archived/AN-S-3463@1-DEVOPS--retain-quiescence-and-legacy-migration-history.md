---
atom_family: SPEC
atom_id: AN-S-3463
container:
  component: C16
tier: 3
context:
  lens: DevOps
state:
  status: archived
  version: 1
  updated_at: 2026-10-09 16:24:06 +0400
---
## Summary

Retain quiescence and legacy migration history

# Summary

Retain quiescence and legacy migration history

## Scope

The evidence that migration stopped only owned processes safely and preserved old N/history.

## Claim

the INSTALL_TOOLS facade **must** quiesce **only** an exactly identified owned process before migration switch and **must** retain old state and N/history when quiescence is unsafe, blocked or incomplete.

## Details

`quiescence.toml` records each proposed process's owned subtree, package/context/generation proof, command digest, start token, requested shutdown, observed response and deadline. A PID absent its matching command and generation proof is not owned. Unknown, changed, externally owned, ambiguous or non-responsive processes block migration without signaling, killing or replacing them.

`history.toml` retains prior selector bytes, N/history references, inventory digest and terminal migration outcome. It is append-only for migration attempts and does not authorize deletion. The canonical Journal records actual start and terminal evidence separately; this carrier is not another Journal.
