---
atom_family: SPEC
atom_id: AN-S-1380
container:
  component: C21
tier: 1
context:
  lens: DES
state:
  status: archived
  version: 22
  updated_at: 2026-11-09 21:15:45 +0400
---

## Summary

Fail closed on invalid Tool projections

## Claim

### Prose Claim

MCP **must** fail closed for each invalid Tool **or** Workflow descriptor. A missing contract field, name collision, invalid canonical-model-derived schema, unresolved binding, **or** ambiguous capability identity **must** make only that capability unavailable with explicit diagnostics. MCP **must not** expose the invalid capability, retain its stale projection as current, **or** reinterpret it as another capability.

MCP **must** publish the complete set of independently valid current descriptors despite an unrelated invalid descriptor. One quarantined capability **must not** disable, withdraw, **or** misrepresent an unrelated valid Tool **or** Workflow binding. Registry output **must** identify each unavailable capability and its attributable diagnostic without claiming that client refresh has occurred.

## Details

Retain the complete candidate frontier and identify the invalid capability and exact field. Quarantine it, remove its stale projection, emit its diagnostic without repairing, invoking, or reinterpreting it, and publish independently valid descriptors in the same generation. Stop the whole registry only when generator integrity or the common activated descriptor frontier is unresolved.
