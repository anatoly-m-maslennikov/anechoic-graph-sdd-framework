---
atom_family: SPEC
atom_id: AN-S-1387
container:
  component: C21
tier: 1
context:
  lens: DES
state:
  status: active
  version: 21
  updated_at: 2026-11-10 20:47:54 +0400
---

## Summary

Return stable model-readable MCP results

## Claim

### Prose Claim

MCP **must** map Tool results, diagnostics, empty results, partial results, **and** failures into stable model-readable protocol responses while preserving their governed meaning **and** provenance. Responses **must** remain usable **without** a user interface, distinguish protocol failure from Tool failure, **and** **must not** expose internal implementation details as part of the public MCP contract.

## Details

### Result projection

#### Applicable when

Apply **after** one canonical Tool returns an admitted outcome.

#### Procedure

1. Map the Tool result, diagnostic, empty result, partial result, **or** failure **to** the declared protocol result form.
2. Preserve the original governed meaning **and** provenance.
3. Distinguish a protocol failure from a Tool failure **and** omit internal implementation details from the public response.

#### Outcome

the model receives a stable, headless-readable result that retains the Tool outcome's meaning.

#### Failure or stop

Stop **and** return an explicit protocol failure **when** the result cannot be represented **without** semantic loss **or** boundary leakage.
