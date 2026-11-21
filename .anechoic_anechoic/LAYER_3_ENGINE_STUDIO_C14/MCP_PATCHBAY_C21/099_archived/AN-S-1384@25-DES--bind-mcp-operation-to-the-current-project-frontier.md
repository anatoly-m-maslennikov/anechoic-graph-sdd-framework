---
atom_family: SPEC
atom_id: AN-S-1384
structure:
  container:
    component: C21
  tier: 1
context:
  lens: DES
state:
  status: "archived"
  version: 25
  updated_at: "2026-11-21T10:39:47.705687+00:00"
---
## Summary

Bind MCP operation to the current project frontier

## Claim

### Prose Claim

A legacy one-Project MCP service instance **must** bind **to** exactly one resolved ANECHOIC Project root, selected installed Tool release, and generated code/configuration MCP registry revision. In the shared service, native Tool execution/invocation **must** bind **to** exactly one validated Project identity and installed code/configuration frontier. Host-scoped Tool discovery **may** publish the initial union of compatible Project frontiers with per-Project source/revision provenance, but the union is not a selected Project. Discovery and results expose enough installed-code and generated-registry provenance to diagnose currentness; cross-project path escape, unresolved identity, or stale-registry invocation fails explicitly.

The legacy launcher remains one-Project; shared discovery union is not a selected Project and each native execution remains bound to one validated identity/frontier. Registration and generic invocation do not reread source Atoms to prove currentness; each backend operation retains its own source/business validation.
