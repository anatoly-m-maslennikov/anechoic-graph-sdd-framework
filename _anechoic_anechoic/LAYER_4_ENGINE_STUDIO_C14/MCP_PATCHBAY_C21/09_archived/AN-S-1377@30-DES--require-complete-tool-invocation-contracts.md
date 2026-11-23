---
atom_family: SPEC
atom_id: AN-S-1377
container:
  component: C21
tier: 1
context:
  lens: DES
state:
  status: archived
  version: 30
  updated_at: 2026-11-09 19:30:15 +0400
---

## Summary

Require complete Tool invocation contracts

## Claim

### Prose Claim

MCP **must** consume the transport-neutral Tool self-description required by `CA-R-1930-TOOLS-RULE--require-uniform-tool-self-description` **without** duplicating or changing its contract. MCP **must** project the canonical descriptor through one uniform provider invoke wrapper and add only MCP transport identity, protocol representation, and transport diagnostics. A Workflow binding admitted through MCP is outside this Tool descriptor contract. Missing, conflicting, **or** ambiguous Tool descriptor fields make **that** Tool invalid for MCP projection.

Descriptor discovery and validation describe capability availability only; they **must not** invoke a Tool, start **or** resume a Workflow, infer approval, or cause an effect.

## Details

Before exposure, MCP calls the Tool's canonical `describe_tool()` implementation, resolves model symbols and the provider adapter only from trusted installed Engine code, and derives schemas from the canonical models. It validates every descriptor field against the same Tool identity and rejects a handwritten duplicate schema, missing or conflicting field, ambiguous binding, or unresolved callable entrypoint with field-level diagnostics. The affected descriptor is unavailable for projection; validation neither repairs or reinterprets it, imports untrusted code, nor invokes the Tool.
