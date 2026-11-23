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
  version: 20
  updated_at: 2026-11-02 19:44:26 +0400
---
## Summary

Negotiate supported MCP protocol capabilities

## Claim

### Prose Claim

MCP **must** declare its supported Model Context Protocol revision **and** capabilities **and** negotiate them during initialization. Unsupported revisions, incompatible required capabilities, **and** invalid lifecycle transitions **must** fail with explicit machine-readable diagnostics rather than silently changing behavior **or** accepting an undefined compatibility mode.
