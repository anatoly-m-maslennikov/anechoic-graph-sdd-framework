---
atom_family: SPEC
atom_id: AN-S-1063
container:
  component: C16
tier: 2
context:
  lens: QA
state:
  status: archived
  version: 17
  updated_at: 2026-10-24 11:58:20 +0400
---
## Summary

Accept registered control-root carriers

# Accept registered control-root carriers

## Test case

**Fixture:** keep **only** registered Atom, Journal, Projection, Settings, catalog, map, hub, **and** control-file carriers under the control root.

**Expected result:** pass the control-root carrier allowlist check.
