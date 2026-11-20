---
atom_family: SPEC
atom_id: AN-S-1386
structure:
  container:
    component: C21
  tier: 1
context:
  lens: DES
state:
  status: active
  version: 22
  updated_at: 2026-11-10 20:47:54 +0400
---

## Summary

Enforce least authority and secret boundaries

## Claim

### Prose Claim

MCP **must** grant each projected capability no more authority than its source Tool requires **and** **must** preserve **all** Tool authorization **and** permission checks. Credentials **must** remain bound **to** their admitted transport **and** resource, **and** secrets **must not** appear **in** Tool discovery, model-readable results, diagnostics, logs, progress messages, **or** generated registries.

## Details

### Authorization and secrets

When MCP projects a capability, forwards an invocation, or forms a result:

1. Grant no more authority than the source Tool requires and preserve every authorization/permission check.
2. Bind credentials only to their admitted transport and resource boundary.
3. Exclude secrets from discovery, results, diagnostics, logs, progress, and generated registries.

Expose only the Tool's admitted authority without leaking credentials. Stop the affected projection/invocation when authority broadens or a secret-bearing representation would be emitted.

Sources: Model Context Protocol authorization (https://modelcontextprotocol.io/specification/2025-11-25/basic/authorization); CA-A-057 — Reconcile PROGRAMMATIC specialization authority (../../02_analysis/CA-A-057-PROGRAMMATIC-ANALYSIS_RPRT--reconcile-programmatic-specialization-authority.md).
