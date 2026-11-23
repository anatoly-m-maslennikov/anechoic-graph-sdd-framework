---
atom_family: SPEC
atom_id: AN-S-3520
container:
  component: C16
tier: 3
context:
  lens: DevOps
state:
  status: archived
  version: 2
  updated_at: 2026-10-14 20:53:35 +0400
---
## Summary

Map legacy state copy, verification and switch

# Summary

Map legacy state copy, verification and switch

## Scope

The loss-avoiding transfer of the three owned legacy subtrees to installation runtime state.

## Claim

the INSTALL_TOOLS facade **must** copy, verify and retain each owned legacy subtree **before** switching the target selector, and **must not** delete legacy state during migration.

## Details

`mapping.toml` has three exact roots: `project_mcp -> runtime/project_mcp`, `mcp_hot_reload -> runtime/mcp_hot_reload`, and `workflow_orchestrator -> runtime/workflow_orchestrator`, all beneath the migration directory. `copy-proof.toml` records source and destination ordered inventory digests, and `switch.toml` records previous selector SHA-256, replacement selector SHA-256, prior N/history references and state generation.

Copy uses staging beneath the migration root, rejects changed inventory rows and verifies byte and mode equality before atomic switch under CA-D-603. The old subtrees remain at their original paths, remain readable for recovery and are named by inventory proof. A partial copy, denied switch or terminal-recording failure retains actual state without claiming migration completion.
