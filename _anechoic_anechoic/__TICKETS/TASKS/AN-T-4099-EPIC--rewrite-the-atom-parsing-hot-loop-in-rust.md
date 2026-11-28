---
atom_family: TKT
atom_id: AN-T-4099
container:
  component: C00
priority: 2
context:
  template: task
  label: Epic
state:
  status: in_queue
  version: 1
  updated_at: '2026-11-28T09:57:46+00:00'
---

## Summary

Rewrite the Atom parsing hot loop in Rust

## Objective

Reduce the time ANECHOIC spends parsing Atoms during source capture.

## Tasks

1. Profile Atom parsing in a full capture and a small incremental refresh. Identify the hot loop and record the Python baseline.
2. Find a Rust library for the measured parsing step. Test candidates against existing Atom fixtures. Compare behavior, speed, maintenance, license, and build cost.
3. Rewrite the measured hot loop in Rust. Preserve the caller contract, parsed values, source locations, and diagnostics.
4. Compare parse time, capture time, and peak memory on the same Project snapshot. Adopt the Rust path if parity holds and the end-to-end gain justifies the build and release cost.
