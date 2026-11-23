---
atom_family: SPEC
atom_id: AN-S-231
container:
  component: C16
tier: 4
context:
  lens: QA
state:
  status: archived
  version: 11
  updated_at: 2026-10-23 03:17:34 +0400
---
## Summary

Reject stale Projection

# Reject stale Projection

## Test case

**Fixture:** change a Projection source **after** its recorded `source_frontier` **without** rebuilding the Projection.

**Expected result:** fail with the stable stale-Projection diagnostic **and** a non-zero exit.
