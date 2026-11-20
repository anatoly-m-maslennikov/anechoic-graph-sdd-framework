---
identity:
  atom_id: AN-S-1919
context:
  container:
    component: C21
  tier: 3
  lens: QA
state:
  status: active
  version: 24
  updated_at: '2026-11-12T01:59:14.433341+00:00'
---

## Summary

Cancel one bounded MCP request without orphaning work

## Claim

### Prose Claim

MCP cancellation terminates one admitted bounded request **without** corrupting state **or** leaving ungoverned work.

## Details

### Test case

Cancel one admitted long-running request with a progress identity **before** its
declared completion boundary, **then** deliver one late downstream completion.

### Acceptance criteria

pass **only** **when** the adapter stops **or** isolates downstream work, releases bounded
resources, emits no successful terminal result, keeps Tool **and** project state
valid, **and** the late completion cannot revive the cancelled request.

### Atom Lifecycle cancellation

Exercise cancellation while input is pending, while waiting to start an effect, and after an effect starts in a single or composed lifecycle call. Before an effect starts, cancel without changing a carrier. After dispatch, verify that an in-flight Action reaches its own outcome safely, the canceled request reports no success, and effects that already completed remain observable. Check the known partial state after interruption between lifecycle effects. Run a streaming HTTP client case as well as controlled stage tests.

### Failure disposition

Stop **and** diagnose the request boundary **before** another dispatch.

### Sources

- [Model Context Protocol: cancellation](https://modelcontextprotocol.io/specification/2024-11-05/basic/utilities/cancellation)
- [Model Context Protocol: tasks](https://modelcontextprotocol.io/specification/2025-11-25/basic/utilities/tasks)
- [CA-R-1117 — Bound one admitted MCP request](../04_requirement/CA-R-1117-MCP-RULE--bound-and-control-mcp-requests.md)
