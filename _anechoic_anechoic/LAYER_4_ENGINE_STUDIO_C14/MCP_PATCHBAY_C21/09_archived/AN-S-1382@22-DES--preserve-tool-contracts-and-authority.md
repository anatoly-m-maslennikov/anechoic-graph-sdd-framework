---
atom_family: SPEC
atom_id: AN-S-1382
container:
  component: C21
tier: 1
context:
  lens: DES
state:
  status: archived
  version: 22
  updated_at: 2026-11-09 21:15:45 +0400
---

## Summary

Preserve Tool contracts and authority

## Claim

### Prose Claim

MCP **must** preserve each Tool's accepted inputs, structured outputs, diagnostics, failures, target-set identity, **and** side-effect controls **without** changing their meaning. MCP **must** preserve Finder read-only behavior, Checker evidence **and** verdict behavior, Doer dry-run **and** explicit-apply behavior, **and** **every** Tool permission boundary; it **must** never broaden mutation authority, infer approval, **or** convert a failed **or** partial Tool result into success.

For ANECHOIC Markdown Atom Doers, MCP **must** pass through the canonical Tool's sealed target set, expected revision **or** digest, Initiative action envelope, **and** resulting receipt. It **must not** replace a Tool's atomic **or** bulk cardinality, preflight, conflict, recovery, **or** lifecycle decision with transport behavior of its own.

## Details

Implement MCP as a replaceable protocol adapter: preserve the canonical request/result contract and pass a Markdown Atom Doer's sealed target set, expected revision or digest, Initiative action, and receipt unchanged. Stop whenever protocol adaptation would broaden authority, alter cardinality, or obscure a Tool failure.
