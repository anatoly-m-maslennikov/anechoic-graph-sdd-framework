---
atom_family: SPEC
atom_id: AN-S-1552
container:
  component: C21
tier: 3
context:
  lens: DevOps
state:
  status: active
  version: 19
  updated_at: 2026-11-10 20:47:54 +0400
---

## Summary

carry Project MCP launch results

## Claim

### Prose Claim

the launcher **must** carry an attributable structured result that exposes a localhost MCP URL only after loopback Host/Origin-protected host readiness and never carries an HTTP credential.

## Details

### Safe launcher result

- Default result carries disposition (started, reused, refused, failed, or busy), exactly one CA-O-235 safe condition code, Project identity and safe root/control-root references, immutable image digest/fingerprint, service state, Docker-observed publication, and readiness disposition. A ready success alone carries one loopback /anechoic/mcp URL; --output url is allowed only then. No Git-repository identity is required.
- Construct the URL only from one Docker-observed 127.0.0.1 publication after successful Host/Origin readiness. Never synthesize a port, return before readiness, or redirect through a proxy.
- Results and ordinary diagnostics omit password, bearer, Authorization, secret environment values, credential-file contents, command arguments, and secret URL components; this transport has no credential source.
- Refusal/failure remains complete structured output with no claimed replacement, queue/worker/Agent/Workflow start, Tool execution, Release effect, or cross-Project fallback. Bounded wait exhaustion is readiness failure, not ready.
