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
  version: 22
  updated_at: "2026-11-27T16:29:34.309627+00:00"
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

#### Failure or stop

Stop **and** return an explicit protocol failure **when** the result cannot be represented **without** semantic loss **or** boundary leakage.
