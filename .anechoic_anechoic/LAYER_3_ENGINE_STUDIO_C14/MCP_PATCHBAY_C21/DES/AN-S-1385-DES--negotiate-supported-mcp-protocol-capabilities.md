---
identity:
  atom_id: AN-S-1385
context:
  container:
    component: C21
  tier: 1
  lens: DES
state:
  status: active
  version: 22
  updated_at: 2026-11-10 20:47:54 +0400
---

## Summary

Negotiate supported MCP protocol capabilities

## Claim

### Prose Claim

MCP **must** declare its supported Model Context Protocol revision **and** capabilities **and** negotiate them during initialization. Unsupported revisions, incompatible required capabilities, **and** invalid lifecycle transitions **must** fail with explicit machine-readable diagnostics rather than silently changing behavior **or** accepting an undefined compatibility mode.

## Details

Compare the peer's required protocol revision and capabilities with the declaration before capability execution.

### Sources

- [Model Context Protocol: lifecycle](https://modelcontextprotocol.io/specification/2025-06-18/basic/lifecycle)
- [CA-A-057 — Reconcile PROGRAMMATIC specialization authority](../02_analysis/CA-A-057-PROGRAMMATIC-ANALYSIS_RPRT--reconcile-programmatic-specialization-authority.md)
