---
atom_family: SPEC
atom_id: AN-S-3519
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

Inventory owned legacy installation subtrees

# Summary

Inventory owned legacy installation subtrees

## Scope

The exact owned legacy state eligible for a retained-state migration.

## Claim

the INSTALL_TOOLS facade **must** inventory **only** `.anechoic_install/project_mcp`, `.anechoic_install/mcp_hot_reload` and `.anechoic_install/workflow_orchestrator` before migration, and **must not** infer ownership from adjacent or similarly named state.

## Details

`.anechoic_runtime/installation/migrations/<migration_id>/inventory.toml` contains schema, target context digest, ordered source-root rows, each relative path, type, SHA-256, mode and owned-process observations. The inventory includes selector and N/history references required to preserve prior runtime provenance, but does not absorb authoring sources, settings, unrelated `.anechoic_install` members, external processes or arbitrary user files.

Symlinks, special files, path traversal, duplicate roots, changed bytes or unproven owner identity reject before copy. The inventory is re-read after quiescence and before switch; it is retained even for a blocked migration.
