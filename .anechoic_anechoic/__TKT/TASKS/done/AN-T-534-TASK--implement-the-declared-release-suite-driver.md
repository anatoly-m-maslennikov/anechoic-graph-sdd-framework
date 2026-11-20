---
identity:
  atom_id: AN-T-534
context:
  container:
    atom: AN-T-538
  tier: 3
  template: task
state:
  status: done
  version: 9
  updated_at: 2026-10-25 17:32:27 +0400
---
# Summary

Implement the declared Release suite driver

## Objective

Implement the accepted complete-suite driver and maintained module-level probe rules.

## Details

Own only RELEASE_VERSION/run_release_suite.py and release_suite_bindings.json. Execute every declared testcase in fresh per-module children, attest exact sealed sources, emit one JUnit row per actual testcase, and fail closed for unavailable prerequisites. Reuse unittest and standard-library facilities. Expected bounded work: <=15 minutes; decompose if needed.

## Definition of Done

The driver satisfies the accepted RMED and deterministic E2E corpus without hidden exclusions or synthetic full-suite success.

## Results

The fixed CLI driver and maintained source-probe rules are saved in 689dd212f. Independent bounded review accepts exact per-testcase reporting, complete sealed-module discovery and truthful incomplete/non-pass states. Twelve golden cases pass; no actual complete Docker suite is claimed.
