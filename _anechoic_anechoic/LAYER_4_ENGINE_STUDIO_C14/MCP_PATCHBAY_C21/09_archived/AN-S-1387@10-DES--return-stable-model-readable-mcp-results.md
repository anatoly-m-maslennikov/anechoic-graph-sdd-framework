---
atom_family: SPEC
atom_id: AN-S-1387
container:
  component: C21
tier: 4
context:
  lens: DES
state:
  status: archived
  version: 10
  updated_at: 2026-10-24 00:28:02 +0400
---
## Summary

Return stable model-readable MCP results

# Return stable model-readable MCP results

MCP **must** map Tool results, diagnostics, empty results, partial results, **and** failures into stable model-readable protocol responses while preserving their governed meaning **and** provenance. Responses **must** remain usable **without** a user interface, distinguish protocol failure from Tool failure, **and** **must not** expose internal implementation details as part of the public MCP contract.
