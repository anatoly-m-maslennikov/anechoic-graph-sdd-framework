---
atom_family: SPEC
atom_id: AN-S-1302
structure:
  container:
    component: C15
  tier: 5
context:
  lens: QA
state:
  status: active
  version: 22
  updated_at: 2026-11-10 20:47:54 +0400
---
## Summary

Preserve the last valid MCP frontier

## Claim

### Prose Claim

An invalid MCP frontier refresh rejects the candidate, reports its active-Tool collision, and preserves preceding complete valid bytes only for recovery—not as current or call authorization. Replacement is atomic at the validated frontier boundary.
