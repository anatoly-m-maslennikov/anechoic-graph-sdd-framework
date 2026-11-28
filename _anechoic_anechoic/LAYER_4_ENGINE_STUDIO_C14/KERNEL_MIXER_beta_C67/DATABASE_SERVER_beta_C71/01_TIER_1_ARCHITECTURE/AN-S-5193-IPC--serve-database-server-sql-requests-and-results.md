---
atom_family: SPEC
atom_id: AN-S-5193
container:
  component: C71
tier: 1
context:
  lens: SWD/INTERNAL_API/IPC
state:
  status: active
  version: 2
  updated_at: "2026-11-28T15:16:37.698017+00:00"
---

## Summary

Serve Database Server SQL requests and results

## Claim

Serve one read-only SELECT
per request with no external access and at most 1,000 rows.

Return cached rows inline or disposable Project files. Export full Run
or requested Page or View Fetch as JSON matrix, CSV, or TOON, preserving
positions and column names. On export failure return partial with the
query ID and retain the result. Apply Run preview before materialization
and retain it at refresh. Apply Page and Fetch previews only to delivery.
