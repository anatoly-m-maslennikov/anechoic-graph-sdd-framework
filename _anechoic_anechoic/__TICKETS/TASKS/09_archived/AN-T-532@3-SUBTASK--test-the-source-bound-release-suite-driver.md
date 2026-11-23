---
atom_family: TKT
atom_id: AN-T-532
container:
  component: C00
priority: 2
context:
  template: task
  label: Subtask
state:
  status: archived
  version: 3
  updated_at: 2026-10-24 08:16:43 +0400
---
## Summary

Test the source-bound Release suite driver

# Summary

Test the source-bound Release suite driver

## Objective

Build deterministic E2E golden fixtures for the accepted suite driver before accepting its implementation.

## Details

Own only RELEASE_VERSION/tests/test_run_release_suite.py and tests/full_suite_golden/. Exercise the exact sealed CLI environment: complete testcase discovery, source digests, immutable envelope, six groups and compiled evidence, and failure/skip/omission/duplicate/unsafe input. Keep the fixture outputs retained. Expected bounded work: <=15 minutes; decompose if needed.

## Definition of Done

The unchanged golden corpus passes against the implemented driver; positive cases are executed and negative cases cannot produce a passing gate.

## Results

Twelve golden driver cases pass with the exact host interpreter. Stored intentional test payloads use fixture-prefixed names; the disposable loader restores their intended names. Positive discovery and negative failure, skip, zero-case, duplicate, unsafe-input and schema-2 cases remain covered without production exclusions.
