---
atom_family: SPEC
atom_id: AN-S-3575
container:
  component: C15
tier: 1
context:
  lens: QA
state:
  status: archived
  version: 9
  updated_at: 2026-10-26 00:46:35 +0400
---
## Summary

Bound and recover canary exposure

# Summary

Bound and recover canary exposure

## Scope

Canary Evaluation of a changed PROGRAMMATIC component against a production-like or live workload.

## Claim

Canary Evaluation **may** be admitted **only when** the cohort **or** shadow surface isolates exposure; exposure is bounded; immediate stop is available; **and** rollback has been tested against the applicable state boundary. Canary evidence supplements rather than replaces required pre-deployment evidence.

## Details

These are necessary safety conditions, not a complete canary technique specification.

## Sources

- [CA-E-536@2 — historical extraction basis](archive/CA-E-536-PROGRAMMATIC-CORE-EVAL_APPROACH--admit-safe-canary-evaluation@2.md)
