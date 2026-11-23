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
  version: 20
  updated_at: 2026-10-27 19:59:50 +0400
---
## Summary

Fail closed on invalid Tool projections

# Fail closed on invalid Tool projections

MCP **must** fail closed for each invalid Tool **or** Workflow descriptor. A missing contract field, name collision, invalid canonical-model-derived schema, unresolved binding, **or** ambiguous capability identity **must** make only that capability unavailable with explicit diagnostics. MCP **must not** expose the invalid capability, retain its stale projection as current, **or** reinterpret it as another capability.

MCP **must** publish the complete set of independently valid current descriptors despite an unrelated invalid descriptor. One quarantined capability **must not** disable, withdraw, **or** misrepresent an unrelated valid Tool **or** Workflow binding. Registry output **must** identify each unavailable capability and its attributable diagnostic without claiming that client refresh has occurred.
