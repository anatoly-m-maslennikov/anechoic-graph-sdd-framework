---
atom_family: SPEC
atom_id: AN-S-1391
container:
  component: C21
tier: 1
context:
  lens: DES
state:
  status: "archived"
  version: 2
  updated_at: "2026-11-22T08:29:26.025756+00:00"
---

## Summary

MCP exposes the active Tool registry

## Claim

### Prose Claim

MCP must read the generated registration asset carried by the installed package, resolve only its code-owned provider entries, and apply the bound Project's configured exclusions. It must expose the resulting enabled installed code/configuration surface through existing backend adapters. Atom status, Subjects, Scope Unit graphs, Tool-folder discovery, and unlisted implementation helpers do not determine runtime exposure. Missing or malformed registration configuration is reported explicitly; MCP must not fall back to Atom discovery.

Load the installed registration asset when MCP starts or explicitly loads a rebuilt installed implementation.

The installed registration configuration must carry an explicit `mcp_blacklist` of exact public Tool names. Blacklisted Tools must not be exposed through MCP or admitted by direct MCP invocation. Bound Project exclusions may further restrict exposure; they cannot re-enable a globally blacklisted Tool. An internal or CLI implementation may remain installed without MCP exposure.
