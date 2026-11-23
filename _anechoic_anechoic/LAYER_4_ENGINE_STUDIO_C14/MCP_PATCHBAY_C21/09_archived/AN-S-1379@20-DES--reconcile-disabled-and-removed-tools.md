---
atom_family: SPEC
atom_id: AN-S-1379
container:
  component: C21
tier: 1
context:
  lens: DES
state:
  status: archived
  version: 20
  updated_at: 2026-11-02 19:44:26 +0400
---
## Summary

Reconcile disabled and removed Tools

## Claim

### Prose Claim

MCP regeneration **must** add **every** newly active valid Tool, exclude **every** explicitly disabled Tool, **and** remove **every** projection whose source Tool is no longer active **or** present. MCP **must not** maintain a second independent allowlist **or** lifecycle registry that can disagree with current project authority **and** Configuration.
