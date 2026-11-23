---
atom_family: SPEC
atom_id: AN-S-3875
container:
  component: C21
tier: 2
context:
  lens: SWD
state:
  status: archived
  version: 12
  updated_at: 2026-10-24 06:07:28 +0400
---
## Summary

Preserve one Tool contract and authority boundary

# Preserve one Tool contract and authority boundary

## Applicable when

Apply while MCP adapts one canonical Tool request **or** result **to** protocol transport.

## Procedure

1. Implement MCP as a replaceable protocol adapter **and** keep project meaning
   **and** business decisions outside the carrier.
2. Preserve accepted inputs, results, diagnostics, failures, target-set identity, **and** side-effect controls exactly.
3. Pass a ANECHOIC Markdown Atom Doer's sealed target set, expected revision **or** digest, Initiative action, **and** receipt through unchanged.
4. Keep Finder, Checker, **and** Doer boundaries intact; do **not** infer approval **or** turn a failed **or** partial result into success.

## Outcome

Transport changes representation **only**, never Tool authority **or** semantics.

## Failure or stop

Stop whenever protocol adaptation would broaden authority, alter cardinality, **or** obscure a Tool failure.

## Sources

- [Model Context Protocol: base protocol](https://modelcontextprotocol.io/specification/2025-06-18/basic/index)
- [PEP 544 — Protocols](https://peps.python.org/pep-0544/)
- [CA-A-057 — Reconcile PROGRAMMATIC specialization authority](../../02_analysis/CA-A-057-PROGRAMMATIC-ANALYSIS_RPRT--reconcile-programmatic-specialization-authority.md)
