---
atom_family: SPEC
atom_id: AN-S-3881
container:
  component: C21
tier: 2
context:
  lens: SWD
state:
  status: archived
  version: 10
  updated_at: 2026-10-24 01:28:26 +0400
---
## Summary

Preserve least-authority and secret boundaries

# Preserve least-authority and secret boundaries

## Applicable when

Apply **when** MCP projects a capability, forwards an invocation, **or** forms a result.

## Procedure

1. Grant no more authority than the source Tool requires **and** preserve its authorization checks.
2. Bind credentials **only** **to** their admitted transport **and** resource boundary.
3. Exclude secrets from discovery, results, diagnostics, logs, progress, **and** generated registries.

## Outcome

MCP exposes **only** the Tool's admitted authority **without** leaking credentials.

## Failure or stop

Stop the affected projection **or** invocation **when** authority is broadened **or** a secret-bearing representation would be emitted.

## Sources

- [Model Context Protocol: authorization](https://modelcontextprotocol.io/specification/2025-11-25/basic/authorization)
- [CA-A-057 — Reconcile PROGRAMMATIC specialization authority](../../02_analysis/CA-A-057-PROGRAMMATIC-ANALYSIS_RPRT--reconcile-programmatic-specialization-authority.md)
