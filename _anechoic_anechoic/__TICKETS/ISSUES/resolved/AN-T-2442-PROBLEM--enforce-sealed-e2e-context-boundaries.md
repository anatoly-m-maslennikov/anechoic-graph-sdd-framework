---
atom_family: TKT
atom_id: AN-T-2442
container:
  component: C16
priority: 2
context:
  template: problem
state:
  status: resolved
  version: 3
  updated_at: 2026-10-23 01:47:30 +0400
---
# Summary

Enforce sealed E2E context boundaries

## Concern

The real-loader golden tests reject malformed context bindings but accept a scratch root equal to the source root and arbitrary Harness admission values, contrary to D582's dedicated scratch and fixed per-Harness context.

## Evidences

The focused context suite ran 13 cases: 11 passed, while two enforcing cases failed because ReleaseE2EContextError was not raised. No loader mock or Docker was used.

## Blast radius

P1751 behavioral acceptance and the separately admitted Candidate E2E/Full Gate boundary. Real Docker and runtime installation remain separately unproved.

## Disposition

Require a strict executor-owned scratch descendant and the exact fixed opt-in keys/values for each of the three Harnesses, including the sealed immutable candidate image. Preserve the enforcing tests and independently review the code.

## Resolution

The actual loader now enforces dedicated strict-descendant scratch/report roots, an inside-scratch context Carrier and exact fixed image-bound Harness opt-ins. Thirteen real loader cases pass after the two enforcing REDs. Independent bounded source review accepts the repair. Root's combined context, Driver and phase-map run passes 24/24; five Runtime binding tests and two actual MCP transport tests also pass separately. Code is saved in 5e0dfee93. This resolves only the named defect; actual Docker E2E and whole Full Gate acceptance remain unfinished.
