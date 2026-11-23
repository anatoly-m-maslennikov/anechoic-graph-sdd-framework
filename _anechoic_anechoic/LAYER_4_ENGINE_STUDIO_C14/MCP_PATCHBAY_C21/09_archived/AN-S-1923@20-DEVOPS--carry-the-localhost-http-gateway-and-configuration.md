---
atom_family: SPEC
atom_id: AN-S-1923
container:
  component: C21
tier: 5
context:
  lens: DevOps
state:
  status: archived
  version: 20
  updated_at: 2026-11-10 20:47:54 +0400
---

## Summary

carry the localhost HTTP Gateway and configuration

## Claim

### Prose Claim

the additional HTTP endpoint **must** be carried by the existing MCP Gateway entrypoint and an opt-in Docker service, with explicit-or-Docker-owned-loopback publication.

## Details

### HTTP Gateway and service

1. Deliver HTTP beside hot_reload.py; keep server.py --transport stdio default. The added transport is streamable-http, path /anechoic/mcp, container port 8092.
2. Keep existing mcp Compose service unchanged. Add opt-in mcp-http with the restricted image and Project mounts, no Docker socket, and a dedicated loopback Host/Origin-protected health check.
3. Explicit docker/mcp-http.compose.yaml publishes only mcp-http on loopback. A lifecycle request may select an integer host port in 1..65535; the bounded Project launcher uses the required Project Settings `[project_mcp] http_port` on `127.0.0.1:<http_port>:8092`; a supplied `--port` must equal that value, missing or invalid settings stop before Docker effects, and an occupied port fails without an alternative. Docker allocates atomically; no pre-bind/probe-reserve/inference. Attach only mcp-http to non-internal http_publication beside runtime; it permits HTTP-service outbound traffic and is not ingress-only. Worker/Agent/stdio attachments and normal startup remain unchanged.
4. Do not configure, read, inject, rotate, or persist HTTP password, bearer, Authorization, secret-file, or credential-environment values.
5. Support mcp-http-start, -stop, and -status. Return the safe URL/state only after exactly one running healthy mcp-http, exactly one TCP publisher to 8092, and bind 127.0.0.1, with caller-selected or observed port. Missing/ambiguous/mismatched publication fails even if health passes; the launcher additionally requires host-side Host/Origin readiness. HTTP startup starts no Codex Agent, worker, queue, Agent, or Workflow.
6. Permit loopback Host and loopback HTTP Origins; non-browser clients need no Origin. Do not require/validate Authorization and expose no credential value.
7. Test in 204_MCP/tests/test_hot_reload_http.py and Docker HTTP configuration/lifecycle tests; retain stdio tests. Docker absence/denial is failed/incomplete real-container evidence, not a fixture pass.
