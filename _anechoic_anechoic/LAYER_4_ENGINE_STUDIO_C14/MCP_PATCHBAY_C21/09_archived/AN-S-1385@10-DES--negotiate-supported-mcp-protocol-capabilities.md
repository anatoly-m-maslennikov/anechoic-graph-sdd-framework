---
atom_family: SPEC
atom_id: AN-S-1385
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

Negotiate supported MCP protocol capabilities

# Negotiate supported MCP protocol capabilities

MCP **must** declare its supported Model Context Protocol revision **and** capabilities **and** negotiate them during initialization. Unsupported revisions, incompatible required capabilities, **and** invalid lifecycle transitions **must** fail with explicit machine-readable diagnostics rather than silently changing behavior **or** accepting an undefined compatibility mode.
