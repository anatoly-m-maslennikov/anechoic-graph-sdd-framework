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
  version: 24
  updated_at: 2026-10-25 17:32:27 +0400
---
## Summary

Require complete Tool invocation contracts

# Require complete Tool invocation contracts

MCP **must** consume the transport-neutral Tool self-description required by `CA-R-1930-TOOLS-RULE--require-uniform-tool-self-description` **without** duplicating or changing its contract. MCP **must** project the canonical descriptor through one uniform provider invoke wrapper and add only MCP transport identity, protocol representation, and transport diagnostics. A Workflow binding admitted through MCP is outside this Tool descriptor contract. Missing, conflicting, **or** ambiguous Tool descriptor fields make **that** Tool invalid for MCP projection.

Descriptor discovery and validation describe capability availability only; they **must not** invoke a Tool, start **or** resume a Workflow, infer approval, or cause an effect.
