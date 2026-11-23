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
  version: 18
  updated_at: 2026-10-26 00:46:35 +0400
---
## Summary

Preserve Tool contracts and authority

# Preserve Tool contracts and authority

MCP **must** preserve each Tool's accepted inputs, structured outputs, diagnostics, failures, target-set identity, **and** side-effect controls **without** changing their meaning. MCP **must** preserve Finder read-only behavior, Checker evidence **and** verdict behavior, Doer dry-run **and** explicit-apply behavior, **and** **every** Tool permission boundary; it **must** never broaden mutation authority, infer approval, **or** convert a failed **or** partial Tool result into success.

For ANECHOIC Markdown Atom Doers, MCP **must** pass through the canonical Tool's sealed target set, expected revision **or** digest, Initiative action envelope, **and** resulting receipt. It **must not** replace a Tool's atomic **or** bulk cardinality, preflight, conflict, recovery, **or** lifecycle decision with transport behavior of its own.
