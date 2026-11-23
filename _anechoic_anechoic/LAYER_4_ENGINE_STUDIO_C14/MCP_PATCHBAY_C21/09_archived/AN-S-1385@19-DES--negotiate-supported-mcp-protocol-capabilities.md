---
atom_family: SPEC
atom_id: AN-S-1385
container:
  component: C21
tier: 1
context:
  lens: DES
state:
  status: archived
  version: 19
  updated_at: 2026-10-27 19:59:50 +0400
---
## Summary

Negotiate supported MCP protocol capabilities

# Negotiate supported MCP protocol capabilities

MCP **must** declare its supported Model Context Protocol revision **and** capabilities **and** negotiate them during initialization. Unsupported revisions, incompatible required capabilities, **and** invalid lifecycle transitions **must** fail with explicit machine-readable diagnostics rather than silently changing behavior **or** accepting an undefined compatibility mode.
