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
  version: 21
  updated_at: 2026-11-09 21:15:45 +0400
---

## Summary

Reconcile disabled and removed Tools

## Claim

### Prose Claim

MCP regeneration **must** add **every** newly active valid Tool, exclude **every** explicitly disabled Tool, **and** remove **every** projection whose source Tool is no longer active **or** present. MCP **must not** maintain a second independent allowlist **or** lifecycle registry that can disagree with current project authority **and** Configuration.

## Details

Load the generated registration asset and configured exclusions; publish its complete enabled entry set, remove disabled or removed configured entries, exclude unlisted helpers, and stop on malformed or unresolved registration configuration. Do not scan native Atoms, Scope Unit graphs, or Tool folders for exposure.
