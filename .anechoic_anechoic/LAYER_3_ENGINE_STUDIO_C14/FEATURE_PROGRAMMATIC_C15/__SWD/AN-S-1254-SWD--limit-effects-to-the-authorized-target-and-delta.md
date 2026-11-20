---
atom_family: SPEC
atom_id: AN-S-1254
structure:
  container:
    component: C15
  tier: 1
context:
  lens: SWD
state:
  status: active
  version: 12
  updated_at: 2026-11-10 20:47:54 +0400
---

## Summary

Limit effects to the authorized target and delta

## Claim



### Prose Claim
**To** change state, bind the admitted target, explicit delta and required expected state, then apply **only** that authorized change.

## Details

### Scope

New or changed PROGRAMMATIC implementation, including Tools, Apps, MCP adapters and tests.


- Do not substitute targets, broaden the affected frontier or add semantic operations.
- Observing additional files or state does not grant permission to change them.
- An unresolved, ambiguous, stale or unsupported binding stops the affected change; it does not authorize a fallback target or broader effect.

Source basis: CA-M-376, CA-M-381.
