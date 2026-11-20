---
identity:
  atom_id: AN-S-231
context:
  container:
    component: C16
  tier: 2
  lens: QA
state:
  status: active
  version: 20
  updated_at: 2026-11-02 19:44:26 +0400
---
## Summary

Reject stale Projection

# Reject stale Projection

## Test case

**Fixture:** change a Projection source **after** its recorded `source_frontier` **without** rebuilding the Projection.

**Expected result:** fail with the stable stale-Projection diagnostic **and** a non-zero exit.
