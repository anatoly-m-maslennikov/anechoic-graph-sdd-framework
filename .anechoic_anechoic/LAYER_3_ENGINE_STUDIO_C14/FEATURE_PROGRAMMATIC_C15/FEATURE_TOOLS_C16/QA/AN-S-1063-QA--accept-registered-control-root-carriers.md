---
identity:
  atom_id: AN-S-1063
context:
  container:
    component: C16
  tier: 2
  lens: QA
state:
  status: active
  version: 22
  updated_at: 2026-11-02 19:44:26 +0400
---
## Summary

Accept registered control-root carriers

# Accept registered control-root carriers

## Test case

**Fixture:** keep **only** registered Atom, Journal, Projection, Settings, catalog, map, hub, **and** control-file carriers under the control root.

**Expected result:** pass the control-root carrier allowlist check.
