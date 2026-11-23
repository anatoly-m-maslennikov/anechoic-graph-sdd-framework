---
atom_family: TKT
atom_id: AN-T-516
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

Enforce settings-backed host E2E execution limits

# Summary

Enforce settings-backed host E2E execution limits

## Objective

Resolve exactly D582's six Framework Instance settings with individual canonical defaults. Enforce inspect, harness and cleanup timeouts and stdout/stderr/JUnit caps while reading; overflow, timeout and uncertain cleanup are non-passing. Bind the current settings and refuse before/after changes; retained disposable directories alone are allowed.

## Details

Ownership: RELEASE_VERSION/release_e2e_gate.py plus private context/Driver only if needed. Expected execution slice <=15 minutes. Workers share the checkout and preserve edits outside their exclusive scope. Root owns integration and Git. Source/currentness, permission and missing evidence guards remain intact.

## Definition of Done

Six-setting fallback/type/finite/positive/overflow/timeout/cleanup tests pass; no caller override or invented seventh setting is admitted.

## Pre-execution review

Root selects this bounded decomposition to finish the accepted R1890/M346/E589/D582 contract, not a narrower smoke-test substitute. Existing retained N, public routes, pending Runs and canonical Journal history remain protected.

## Recorded verification

Local implementation acceptance is saved in 7874fc864 and 5e0dfee93. The complete private gate module passed 11/11 tests after bounded failed/malformed/empty JUnit retention was fixed; the affected method also passed independently. Narrow D582#10 review accepted the final branch. Earlier context/Driver/phase-map, Runtime image-binding and actual stdio transport results remain retained. Synthetic image/command observations are mock data, not Docker or Release proof. No full-suite, installation, promotion or retirement result is claimed.
