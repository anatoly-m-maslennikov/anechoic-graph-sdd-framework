---
atom_family: SPEC
atom_id: AN-S-3502
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

Defer legacy cleanup to later exact approval

# Summary

Defer legacy cleanup to later exact approval

## Scope

the removal boundary after a completed retained-state migration.

## Claim

the INSTALL_TOOLS facade **must** remove legacy carriers **only** under a later exact Operator-approved inventory, and **must not** remove, move or glob-clean any carrier during installation or migration.

## Details

The cleanup approval binds migration ID, inventory digest, target context, ordered paths and approval digest. Every row and quiescence state is reopened immediately before deletion. Missing or changed approval, state or terminal recording refuses without deletion and preserves migration evidence.
