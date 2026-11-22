---
atom_family: SPEC
atom_id: AN-S-1936
container:
  component: C21
tier: 2
context:
  lens: SWD
state:
  status: "archived"
  version: 10
  updated_at: "2026-11-22T08:47:49.125148+00:00"
---
## Summary

Register MCP tools from installed code and generated configuration

## Claim

### Prose Claim

MCP exposure comes from installed code and configuration. Maintain an explicit code-owned provider inventory and generate the deterministic registration asset in refresh mode before image assembly. In existing mode, use the checkout registration asset unchanged. Derive descriptions and typed schemas from provider code, never Atom content, Tool folders, Project scans, or source-Workflow manifests.

At startup load that asset and register enabled providers/routes. A source Atom edit alone cannot change exposure; preserve Project selection, global/configured exclusions, duplicate-name checks, typed request/result validation, and public protocols. Each operation retains its own business validation; route exposure does not assert prerequisites. Native Workbench tools remain available through installed registrations, while retired adapters stay absent.

Single-Project and shared MCP runtimes require an active native Project
Manifest. Workbench and query operations use its native Project owner.

A missing/invalid asset is an explicit configuration error: do not fall back to Atom discovery. tools/list describes admitted registration after exclusions and does not authorize providers. Code changes require a normal server/container restart. MCP and Workbench are transport adapters over the same in-process backend/canonical Tool APIs; MCP translates protocol data but adds no business copy, internal HTTP hop, or second server. Use the official MCP Python SDK.

Keep provider/factory and descriptor-factory bindings in the editable installed inventory. Generate names/schemas from installed provider code; adding or changing a provider and regenerating must not require a central gateway allowlist/dispatch branch. Apply global mcp_blacklist and bound Project exclusions at publication and on every invocation.
