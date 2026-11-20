---
identity:
  atom_id: AN-S-1377
context:
  container:
    component: C21
  tier: 1
  lens: DES
state:
  status: active
  version: 31
  updated_at: 2026-11-10 20:47:54 +0400
---

## Summary

Require complete Tool invocation contracts

## Claim

### Prose Claim

MCP **must** consume the transport-neutral Tool self-description required by `CA-R-1930-TOOLS-RULE--require-uniform-tool-self-description` **without** duplicating or changing its contract. MCP **must** project the canonical descriptor through one uniform provider invoke wrapper and add only MCP transport identity, protocol representation, and transport diagnostics. A Workflow binding admitted through MCP is outside this Tool descriptor contract. Missing, conflicting, **or** ambiguous Tool descriptor fields make **that** Tool invalid for MCP projection.

Descriptor discovery and validation describe capability availability only; they **must not** invoke a Tool, start **or** resume a Workflow, infer approval, or cause an effect.

## Details

Before exposure, call the Tool's canonical describe_tool() from trusted installed Engine code, resolve model symbols/provider adapter there, and derive schemas from canonical models. Validate every descriptor field against the same Tool identity; reject handwritten duplicate schemas, missing/conflicting/ambiguous fields, or unresolved entrypoints with field-level diagnostics. The affected descriptor is unavailable; validation neither repairs/reinterprets it, imports untrusted code, nor invokes a Tool or Workflow.
