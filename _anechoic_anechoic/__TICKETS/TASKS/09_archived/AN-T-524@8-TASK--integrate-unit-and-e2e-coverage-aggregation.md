---
atom_family: TKT
atom_id: AN-T-524
container:
  component: C00
priority: 2
context:
  template: task
state:
  status: archived
  version: 8
  updated_at: 2026-10-24 20:25:49 +0400
---
## Summary

Integrate Unit and E2E coverage aggregation

# Summary

Integrate Unit and E2E coverage aggregation

## Objective

Require the complete source-pinned Unit plus Candidate E2E partition before Release promotion.

## Details

Own suite phase-map/aggregation implementation and focused tests, distinct from private executor and harness ownership. Every sealed real test module must appear exactly once; re-open actual byte-backed receipts and refuse skipped/missing/duplicate/tampered/cross-candidate outcomes. ETA <=15 minutes.

## Definition of Done

The owned source or implementation is independently accepted and actual scoped verification is saved. Mock or source acceptance does not close live Docker, complete-suite, installation or promotion gates.

## Pre-execution review

Root accepts this bounded decomposition of the Operator-approved host E2E design. Respect the stated dependency and file-ownership boundaries. The existing isolated Unit executor, current public manifest, pending Runs and retained N remain protected.

## Execution result

Scoped implementation complete at `394c7916e`. Final terminal verification: Full Gate 7/7; Unit driver/reference-context/phase/admission 32/32; retained E2E readers 2/2. Independent bounded review accepts the real byte-backed Unit/E2E aggregation and source-pinned complete partition. These are source/mock gates, not a real complete Docker suite or promotion.
