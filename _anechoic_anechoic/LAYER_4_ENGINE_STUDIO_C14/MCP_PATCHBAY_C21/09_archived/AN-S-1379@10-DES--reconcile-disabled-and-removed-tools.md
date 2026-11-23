---
atom_family: SPEC
atom_id: AN-S-1379
container:
  component: C21
tier: 4
context:
  lens: DES
state:
  status: archived
  version: 10
  updated_at: 2026-10-24 00:28:02 +0400
---
## Summary

Reconcile disabled and removed Tools

# Reconcile disabled and removed Tools

MCP regeneration **must** add **every** newly active valid Tool, exclude **every** explicitly disabled Tool, **and** remove **every** projection whose source Tool is no longer active **or** present. MCP **must not** maintain a second independent allowlist **or** lifecycle registry that can disagree with current project authority **and** Configuration.
