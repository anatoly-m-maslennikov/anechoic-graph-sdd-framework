---
atom_family: SPEC
atom_id: AN-S-1960
structure:
  container:
    component: C21
  tier: 4
context:
  lens: QA
state:
  status: active
  version: 2
  updated_at: '2026-11-12T16:57:40.257563+00:00'
---
## Summary

Verify universal tool specific help without execution

## Claim

### Prose Claim

Call standard MCP `tools/list`. Verify that each admitted Tool has the description and input schema from the installed registry, including required fields for a Tool that writes source. A globally blacklisted or Project-excluded Tool is absent. Listing executes no Tool and creates no business Journal Run.
