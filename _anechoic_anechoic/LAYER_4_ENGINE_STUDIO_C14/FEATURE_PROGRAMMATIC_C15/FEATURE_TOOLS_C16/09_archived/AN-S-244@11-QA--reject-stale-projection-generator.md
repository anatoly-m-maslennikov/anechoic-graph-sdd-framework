---
atom_family: SPEC
atom_id: AN-S-244
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

Reject stale Projection generator

# Reject stale Projection generator

## Test case

**Fixture:** change the registered generator digest **without** rebuilding its Projection.

**Expected result:** fail with the stable stale-Projection-generator diagnostic **and** a non-zero exit.
