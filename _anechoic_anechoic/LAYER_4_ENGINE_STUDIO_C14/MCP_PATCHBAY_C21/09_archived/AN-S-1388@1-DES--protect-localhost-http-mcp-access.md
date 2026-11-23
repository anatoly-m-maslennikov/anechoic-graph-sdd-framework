---
atom_family: SPEC
atom_id: AN-S-1388
container:
  component: C21
tier: 3
context:
  lens: DES
state:
  status: archived
  version: 1
  updated_at: 2026-10-09 00:42:28 +0000
---
## Summary

protect localhost HTTP MCP access

# Summary

protect localhost HTTP MCP access

## Scope

the additional localhost HTTP transport for the existing Project MCP Gateway.

## Claim

the HTTP endpoint **must** admit a Request **only** with a valid transport Credential and an admitted Host and Origin, while preserving the existing Operator authorization and Tool permission boundaries.

## Details

1. use a shared local bearer Token, supplied at runtime; it grants transport access, not Operator identity or permission to mutate.
2. publish the Docker port on host loopback **only**. Requests with an absent Origin are allowed for non-browser clients; a present Origin must be loopback-allowlisted.
3. missing configuration, absent or invalid bearer Tokens, hostile Hosts and hostile Origins fail closed before Tool handling.
4. keep Credentials out of discovery, results, diagnostics, logs, command arguments, image contents and committed carriers.
