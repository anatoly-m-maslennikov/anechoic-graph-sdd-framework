---
atom_family: SPEC
atom_id: AN-S-1394
structure:
  container:
    component: C21
  tier: 2
context:
  lens: SWD
state:
  status: active
  version: 2
  updated_at: 2026-11-10 20:47:54 +0400
---

## Summary


Bind MCP calls to ProjectSelection and registration revision

## Claim

### Prose Claim

Resolve one explicit ProjectSelection and the current generated registration revision for each MCP call. Preserve the native request and result, carry the trusted Project root only at the outer schema root, and retain enough provenance to attribute the operation. Reject foreign roots, unresolved bindings and stale registration before invocation; operation-specific source checks remain at the operation boundary.
