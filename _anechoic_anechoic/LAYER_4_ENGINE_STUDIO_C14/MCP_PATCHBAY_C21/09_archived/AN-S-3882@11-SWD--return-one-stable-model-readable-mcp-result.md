---
atom_family: SPEC
atom_id: AN-S-3882
container:
  component: C21
tier: 2
context:
  lens: SWD
state:
  status: archived
  version: 11
  updated_at: 2026-10-24 06:07:28 +0400
---
## Summary

Return one stable model-readable MCP result

# Return one stable model-readable MCP result

## Applicable when

Apply **after** one canonical Tool returns an admitted outcome.

## Procedure

1. Map the Tool result, diagnostic, empty result, partial result, **or** failure **to** the declared protocol result form.
2. Preserve the original governed meaning **and** provenance.
3. Distinguish a protocol failure from a Tool failure **and** omit internal implementation details from the public response.

## Outcome

the model receives a stable, headless-readable result that retains the Tool outcome's meaning.

## Failure or stop

Stop **and** return an explicit protocol failure **when** the result cannot be represented **without** semantic loss **or** boundary leakage.
