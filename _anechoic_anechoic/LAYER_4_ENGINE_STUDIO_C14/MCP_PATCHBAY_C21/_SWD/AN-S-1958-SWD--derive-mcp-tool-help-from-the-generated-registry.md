---
atom_family: SPEC
atom_id: AN-S-1958
container:
  component: C21
tier: 2
context:
  lens: SWD
state:
  status: active
  version: 2
  updated_at: '2026-11-12T16:57:31.214663+00:00'
---
## Summary

Derive mcp tool help from the generated registry

## Claim

### Prose Claim

Use the same generated registry to register public MCP Tools and expose their descriptions and input schemas through `tools/list`. Keep the metadata in the provider descriptors. Apply the global blacklist and Project exclusions when registering Tools.
