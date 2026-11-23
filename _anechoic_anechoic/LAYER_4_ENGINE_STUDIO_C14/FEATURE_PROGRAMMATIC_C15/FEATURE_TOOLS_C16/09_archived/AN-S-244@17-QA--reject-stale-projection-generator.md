---
atom_family: SPEC
atom_id: AN-S-244
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

Reject stale Projection generator

# Reject stale Projection generator

## Test case

**Fixture:** change the registered generator digest **without** rebuilding its Projection.

**Expected result:** fail with the stable stale-Projection-generator diagnostic **and** a non-zero exit.
