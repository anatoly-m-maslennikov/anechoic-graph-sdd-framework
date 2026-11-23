---
atom_family: SPEC
atom_id: AN-S-3879
container:
  component: C21
tier: 4
context:
  lens: SWD
state:
  status: archived
  version: 9
  updated_at: 2026-10-24 00:51:05 +0400
---
## Summary

Negotiate declared MCP protocol capabilities

# Negotiate declared MCP protocol capabilities

## Applicable when

Apply during MCP service initialization.

## Procedure

1. Declare the supported protocol revision **and** capability set.
2. Compare the peer's required revision **and** capabilities with that declaration.
3. Accept **only** a defined compatible mode **and** return machine-readable diagnostics for unsupported **or** invalid lifecycle states.

## Outcome

MCP initialization selects one explicit compatible protocol boundary.

## Failure or stop

Stop on an unsupported revision, incompatible required capability, **or** invalid lifecycle transition.

## Sources

- [Model Context Protocol: lifecycle](https://modelcontextprotocol.io/specification/2025-06-18/basic/lifecycle)
- [CA-A-057 — Reconcile PROGRAMMATIC specialization authority](../../02_analysis/CA-A-057-PROGRAMMATIC-ANALYSIS_RPRT--reconcile-programmatic-specialization-authority.md)
