---
atom_family: SPEC
atom_id: AN-S-3514
container:
  component: C16
tier: 3
context:
  lens: QA
state:
  status: archived
  version: 2
  updated_at: 2026-10-14 20:53:35 +0400
---
## Summary

Verify retained three-subtree migration and safe quiescence

# Summary

Verify retained three-subtree migration and safe quiescence

## Scope

the owned legacy-copy and unsafe-process acceptance matrix.

## Claim

the QA case **must** accept a migration **only** after all three owned subtrees are copied and byte/mode-verified before switch, and **must** block unsafe quiescence without deletion or selector change.

## Details

The success fixture inventories exact roots, proves owned processes through generation/command, copies, verifies, switches and reopens old state and N/history. It injects an adjacent unowned directory, changed row, symlink, process with PID only, external process, timeout and switch interruption; each preserves old state and truthfully reports blocked or partial evidence.
