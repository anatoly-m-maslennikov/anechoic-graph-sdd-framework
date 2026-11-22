---
atom_family: SPEC
atom_id: AN-S-1380
container:
  component: C21
tier: 1
context:
  lens: DES
state:
  status: "active"
  version: 24
  updated_at: "2026-11-22T09:27:00.965129+00:00"
---
## Summary

Fail closed on invalid Tool projections

## Claim

### Prose Claim

Backend must fail closed for each invalid Tool or Workflow descriptor. A missing contract field, name collision, invalid canonical-model-derived schema, unresolved binding, or ambiguous capability identity must make only that capability unavailable with explicit diagnostics. Neither Backend nor MCP may expose the invalid capability, retain its stale projection as current, or reinterpret it as another capability.

Backend must publish the complete set of independently valid current descriptors despite an unrelated invalid descriptor. One quarantined capability must not disable, withdraw, or misrepresent an unrelated valid Tool or Workflow binding. Registry output must identify each unavailable capability and its attributable diagnostic without claiming that client refresh has occurred. MCP maps the valid catalog and reports a missing or invalid catalog explicitly.

## Details

Backend retains the complete candidate frontier, identifies the invalid capability and exact field, removes its stale projection, and publishes independently valid descriptors in the same generation. Generation stops as a whole only when generator integrity or the common activated descriptor frontier is unresolved. Validation does not repair, invoke, or reinterpret a capability.
