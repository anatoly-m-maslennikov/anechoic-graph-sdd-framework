---
atom_family: SPEC
atom_id: AN-S-1550
container:
  component: C21
tier: 3
context:
  lens: DES
state:
  status: archived
  version: 4
  updated_at: 2026-10-24 00:38:25 +0400
---
## Summary

Report server and client refresh separately

# Summary

Report server and client refresh separately

## Scope

server-side hot reload for the Project-local MCP gateway.

## Claim

the MCP gateway **must** distinguish successful server publication from confirmed client discovery of the published Tool registry.

## Details

- publish changed Tool names, schemas **and** descriptions as one validated registry generation.
- announce a changed registry through the negotiated MCP Tool-list-change notification capability.
- notification delivery does **not** prove that Codex refreshed its cached Tool list.
- report client refresh as unconfirmed unless evidence from that client establishes the current registry.
- clients that do **not** refresh require an explicit reconnect; the gateway **must not** claim to modify the Codex desktop application.
- the initial gateway installation requires a reconnect from the currently running server.

