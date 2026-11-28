---
atom_family: SPEC
atom_id: AN-S-1253
container:
  component: C15
tier: 1
context:
  lens: SWD
state:
  status: "active"
  version: 14
  updated_at: "2026-11-27T20:35:14.221449+00:00"
---

## Summary

Keep one canonical owner of behavior

## Claim

### Prose Claim

**To** expose a declared capability through different transports, adapters or storage backends, reuse its canonical behavioral owner rather than independently redefining its meaning.

## Details

### Scope

New or changed PROGRAMMATIC implementation, including Tools, Apps, MCP adapters and tests.


- Adapters translate supported requests and results; they do not invent domain decisions or hidden Workflow composition.
- Keep identity, lifecycle, semantic admission and sequencing with their declared owner.
- Replacing a transport or backend must not silently change the declared capability.

Apply AN-S-2257 to the locality of Requirement and Delivery implementation.
