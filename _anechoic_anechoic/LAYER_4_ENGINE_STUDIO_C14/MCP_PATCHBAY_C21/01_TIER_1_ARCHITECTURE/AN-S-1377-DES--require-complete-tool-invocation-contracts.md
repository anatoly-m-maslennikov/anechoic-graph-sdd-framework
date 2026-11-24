---
atom_family: SPEC
atom_id: AN-S-1377
container:
  component: C21
tier: 1
context:
  lens: DES
state:
  status: active
  version: 32
  updated_at: "2026-11-22T09:26:54.315118+00:00"
---
## Summary

Require complete Tool invocation contracts

## Claim

### Prose Claim

Backend must validate each Tool's canonical transport-neutral self-description before publishing its JSON catalog. MCP must map the published name, description, and input schema to MCP without duplicating or changing the Tool contract. Missing, conflicting, or ambiguous fields make the affected Tool unavailable with explicit diagnostics.

Discovery and validation must not invoke a Tool, start or resume a Workflow, infer approval, or cause an effect. A Workflow binding is outside this Tool descriptor contract.

## Details

Backend resolves trusted installed Tool definitions and canonical models, validates each descriptor against its Tool identity, and rejects unresolved entrypoints and handwritten duplicate schemas. MCP preserves the resulting catalog fields and forwards calls to Backend.
