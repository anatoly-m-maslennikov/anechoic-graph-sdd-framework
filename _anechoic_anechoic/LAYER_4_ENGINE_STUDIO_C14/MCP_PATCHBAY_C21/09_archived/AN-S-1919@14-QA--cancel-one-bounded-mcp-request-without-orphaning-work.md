---
atom_family: SPEC
atom_id: AN-S-1919
container:
  component: C21
tier: 3
context:
  lens: QA
state:
  status: archived
  version: 14
  updated_at: 2026-10-24 11:58:20 +0400
---
## Summary

Cancel one bounded MCP request without orphaning work

# Cancel one bounded MCP request without orphaning work

## Claim checked

MCP cancellation terminates one admitted bounded request **without** corrupting state **or** leaving ungoverned work.

## Test case

Cancel one admitted long-running request with a progress identity **before** its
declared completion boundary, **then** deliver one late downstream completion.

## Acceptance criteria

pass **only** **when** the adapter stops **or** isolates downstream work, releases bounded
resources, emits no successful terminal result, keeps Tool **and** project state
valid, **and** the late completion cannot revive the cancelled request.

## Failure disposition

Stop **and** diagnose the request boundary **before** another dispatch.

## Sources

- [Model Context Protocol: cancellation](https://modelcontextprotocol.io/specification/2024-11-05/basic/utilities/cancellation)
- [Model Context Protocol: tasks](https://modelcontextprotocol.io/specification/2025-11-25/basic/utilities/tasks)
- [CA-M-179 — Bound one admitted MCP request](../05_method/CA-M-179-MCP-METHOD--bound-one-admitted-mcp-request.md)
