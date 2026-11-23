---
atom_family: SPEC
atom_id: AN-S-236
container:
  component: C16
tier: 4
context:
  lens: QA
state:
  status: archived
  version: 15
  updated_at: 2026-10-24 01:18:03 +0400
---
## Summary

Reject duplicate terminal event

# Reject duplicate terminal event

## Test case

**Fixture:** record two terminal Events for the same Work Journal Action identifying one Projection Rebuild under ANECHOIC-GOV-REQU-367. events belonging **to** separately identified rebuild Actions are **not** this duplicate fixture.

**Expected result:** fail the duplicate terminal Events for that Action with the stable duplicate-terminal-event diagnostic **and** a non-zero exit.
