---
atom_family: SPEC
atom_id: AN-S-1959
structure:
  container:
    component: C21
  tier: 3
context:
  lens: DevOps
state:
  status: active
  version: 2
  updated_at: '2026-11-12T16:57:37.459029+00:00'
---
## Summary

Package the shared mcp tool help layer

## Claim

### Prose Claim

The installed MCP package uses its generated `tool_registry.json` to register each admitted Tool with its description and input schema. Standard `tools/list` returns the registered metadata without dispatching Tool execution.
