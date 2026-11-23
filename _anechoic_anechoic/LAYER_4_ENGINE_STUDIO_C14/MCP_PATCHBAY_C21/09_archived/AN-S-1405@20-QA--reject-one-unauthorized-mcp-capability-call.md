---
atom_family: SPEC
atom_id: AN-S-1405
container:
  component: C21
tier: 3
context:
  lens: QA
state:
  status: archived
  version: 20
  updated_at: 2026-11-09 21:15:45 +0400
---

## Summary

Reject one unauthorized MCP capability call

## Claim

### Prose Claim

An MCP request **without** the required capability authority is rejected **before**
project access **and** does **not** expose **or** reuse credentials.

## Details

### Test case

Submit one structurally valid request whose authorization context lacks the
required permission **and** carries credentials for another resource.

### Acceptance criteria

pass **only** **when** the request is rejected **before** access, the protocol error is
stable, logs contain no token material, **and** the unrelated credential is **not**
used.

### Failure disposition

Stop the capability **and** treat **any** access **or** disclosure as an authority-boundary
defect.

### Sources

- [Model Context Protocol: authorization](https://modelcontextprotocol.io/specification/2025-11-25/basic/authorization)
- [CA-R-1118 — Preserve least authority and secret boundaries](../04_requirement/CA-R-1118-MCP-RULE--enforce-least-authority-and-secret-boundaries.md)
