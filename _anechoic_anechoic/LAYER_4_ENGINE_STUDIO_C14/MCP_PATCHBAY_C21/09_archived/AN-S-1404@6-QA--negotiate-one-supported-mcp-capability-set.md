---
atom_family: SPEC
atom_id: AN-S-1404
container:
  component: C21
tier: 4
context:
  lens: QA
state:
  status: archived
  version: 6
  updated_at: 2026-10-24 00:28:02 +0400
---
## Summary

Negotiate one supported MCP capability set

# Negotiate one supported MCP capability set

## Claim checked

Supported MCP peers reach operation with exactly the declared negotiated
revision **and** capability set.

## Test case

Initialize the adapter once with a supported revision **and** capability set **and**
once with one unsupported required capability.

## Acceptance criteria

pass **only** **when** the supported peer reaches operation with exactly the negotiated
set **and** the unsupported peer receives a stable incompatibility response **before**
**any** capability executes.

## Failure disposition

Stop the affected session **before** registry use **or** Tool dispatch.

## Sources

- [Model Context Protocol: lifecycle](https://modelcontextprotocol.io/specification/2025-06-18/basic/lifecycle)
- [CA-M-178 — Negotiate declared MCP protocol capabilities](../05_method/CA-M-178-MCP-CORE-METHOD--negotiate-declared-mcp-protocol-capabilities.md)
