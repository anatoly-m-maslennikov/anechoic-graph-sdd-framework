---
atom_family: SPEC
atom_id: AN-S-1958
container:
  component: C21
tier: 2
context:
  lens: SWD
state:
  status: archived
  version: 1
  updated_at: 2026-11-11 00:16:05 +0400
---

## Summary

Derive mcp tool help from the generated registry

## Claim

### Prose Claim

Provide one shared MCP help layer that identifies the invoked admitted public Tool from the same generated registry used for registration. Derive its help from that registry's canonical schema and short descriptions and examples, including input formats and allowed values, purpose and usage, minimal examples, output contract, and common errors. Keep this metadata with the canonical provider descriptor and generation path; do not create per-Tool handcrafted duplicate help descriptions or a hardcoded Tool-name allowlist.

After trusted Project binding and exclusion checks, route `help: true` to this layer before business input validation or provider execution. Render only the requested Tool's help without calling its capability, running a query or Workflow, changing source, invoking a business gate, or creating a business Journal Run. Preserve the applicable binding envelope and reject invalid bindings without cross-Project fallback; global blacklist and Project exclusions remain effective for help.

Generate each public Tool input schema with an alternative that accepts `help: true` and its required framework Project envelope without normal business-required fields. Protocol-level schema validation must accept that shape before dispatching it to the shared help handler; business validation runs only on the normal invocation branch.
