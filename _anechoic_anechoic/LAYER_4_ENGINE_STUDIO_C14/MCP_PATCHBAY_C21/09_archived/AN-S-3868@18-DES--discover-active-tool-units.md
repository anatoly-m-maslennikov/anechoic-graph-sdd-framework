---
atom_family: SPEC
atom_id: AN-S-3868
container:
  component: C21
tier: 1
context:
  lens: DES
state:
  status: archived
  version: 18
  updated_at: 2026-10-27 06:04:45 +0400
---
## Summary

Discover active Tool units

# Discover active Tool units

MCP **must** discover the complete current set of immediate Tool units owned by `TOOLS` from the current project graph **and** their corresponding Tool folders. Every registered immediate Tool unit is eligible for MCP exposure **unless** current project authority **or** Configuration explicitly disables it; nested implementation helpers **and** folders that are **not** Tool units **must not** become MCP tools.
