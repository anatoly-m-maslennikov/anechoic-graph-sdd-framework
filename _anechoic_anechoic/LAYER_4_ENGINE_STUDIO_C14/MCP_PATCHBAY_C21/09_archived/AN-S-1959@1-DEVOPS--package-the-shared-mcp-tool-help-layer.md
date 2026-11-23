---
atom_family: SPEC
atom_id: AN-S-1959
container:
  component: C21
tier: 3
context:
  lens: DevOps
state:
  status: archived
  version: 1
  updated_at: 2026-11-11 00:16:05 +0400
---

## Summary

Package the shared mcp tool help layer

## Claim

### Prose Claim

The installed MCP package carries the shared help layer and the canonical schema, short descriptions and examples generated with the same `tool_registry.json` used for public registration. The packaged layer provides tool-specific `help: true` output without normal business inputs or Tool execution, while preserving trusted Project binding and global and Project exclusions. Provider additions use the existing inventory and registry generation path, without a central Tool-name allowlist or duplicate per-Tool handcrafted help descriptions. Registry generation and help rendering do not execute capabilities, run queries or Workflows, write source, invoke business gates or create business Journal Runs; technical diagnostics may be recorded.

The generated public input schemas carried by the package admit the `help: true` shape and any required Project envelope without normal business-required fields, before protocol schema rejection and help dispatch.
