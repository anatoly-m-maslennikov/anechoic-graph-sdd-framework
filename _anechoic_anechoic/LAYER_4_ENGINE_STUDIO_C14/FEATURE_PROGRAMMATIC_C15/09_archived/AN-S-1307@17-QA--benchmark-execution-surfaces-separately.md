---
atom_family: SPEC
atom_id: AN-S-1307
container:
  component: C15
tier: 1
context:
  lens: QA
state:
  status: archived
  version: 17
  updated_at: 2026-10-26 00:46:35 +0400
---
## Summary

Benchmark execution surfaces separately

# Benchmark execution surfaces separately

## Claim checked

a performance claim is reproducible for one declared execution surface **and** is
**not** generalized **to** another surface.

## Test case

benchmark one bounded batch Tool workload **and** attempt **to** use that result as the
latency baseline for an interactive Hook.

## Acceptance criteria

pass **only** **when** the batch result preserves command, fixture, runtime, platform,
calibration, distribution, baseline, **and** comparison, while the Hook claim is
rejected as unmeasured.

## Failure disposition

reject unstable **or** cross-surface evidence **and** reopen the affected claim.

## Sources

- [pyperf documentation](https://pyperf.readthedocs.io/en/latest/)
- [CA-M-165 — Measure before optimizing PROGRAMMATIC performance](../05_method/CA-M-165-PROGRAMMATIC-CORE-METHOD--measure-before-optimizing-programmatic-performance.md)
