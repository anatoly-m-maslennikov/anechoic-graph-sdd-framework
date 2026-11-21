---
atom_family: SPEC
atom_id: AN-S-236
structure:
  container:
    component: C16
  tier: 2
context:
  lens: QA
state:
  status: active
  version: 20
  updated_at: 2026-10-27 19:59:29 +0400
---
## Summary

Reject duplicate terminal event

# Reject duplicate terminal event

## Test case

**Fixture:** record two terminal Events for the same Work Journal Action identifying one Projection Rebuild under ANECHOIC-GOV-REQU-367. events belonging **to** separately identified rebuild Actions are **not** this duplicate fixture.

**Expected result:** fail the duplicate terminal Events for that Action with the stable duplicate-terminal-event diagnostic **and** a non-zero exit.
