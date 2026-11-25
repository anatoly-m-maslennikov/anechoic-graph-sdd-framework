---
atom_family: SPEC
atom_id: AN-S-4683
container:
  component: C9
tier: 3
context:
  template: step
  lens: DevOps
state:
  status: archived
  version: 3
  updated_at: 2026-10-05 21:41:23 +0000
---
## Summary

Run the complete candidate release test suite

# Summary

Run the complete candidate release test suite

## Step

This Step invokes CA-O-168 once with phase `run_tests`, binding CA-O-173's complete compiled candidate Projection, the frozen source digest and the full declared release suite.

## Details

The suite must be complete for the declared release boundary; focused, cached, host-only or historical results are not a substitute. It completes before candidate runtime/package or Skill staging and cannot select N+1. A failed, blocked, unsafe, unavailable or unjournalable result stops before staging, image work, promotion or retirement and preserves actual evidence without retry.
