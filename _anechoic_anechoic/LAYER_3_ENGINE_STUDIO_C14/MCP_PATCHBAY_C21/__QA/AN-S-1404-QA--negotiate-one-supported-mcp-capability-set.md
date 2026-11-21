---
atom_family: SPEC
atom_id: AN-S-1404
container:
  component: C21
tier: 3
context:
  lens: QA
state:
  status: active
  version: 21
  updated_at: 2026-11-10 20:47:54 +0400
---

## Summary

Negotiate one supported MCP capability set

## Claim

### Prose Claim

Supported MCP peers reach operation with exactly the declared negotiated
revision **and** capability set.

## Details

### Test case

Initialize the adapter once with a supported revision **and** capability set **and**
once with one unsupported required capability.

### Acceptance criteria

pass **only** **when** the supported peer reaches operation with exactly the negotiated
set **and** the unsupported peer receives a stable incompatibility response **before**
**any** capability executes.

### Failure disposition

Stop the affected session **before** registry use **or** Tool dispatch.

### Sources

- [Model Context Protocol: lifecycle](https://modelcontextprotocol.io/specification/2025-06-18/basic/lifecycle)
- [CA-R-1116 — Negotiate supported MCP protocol capabilities](../04_requirement/CA-R-1116-MCP-RULE--negotiate-supported-mcp-protocol-capabilities.md)
