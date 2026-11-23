---
atom_family: SPEC
atom_id: AN-S-222
container:
  component: C16
tier: 4
context:
  lens: QA
state:
  status: archived
  version: 10
  updated_at: 2026-09-17 21:05:35 +0000
---
## Summary

Reject a childless Principle in strict scope

# Reject a childless Principle in strict scope

## Test case

**Fixture:** leave an Active Principle **without** an active permitted child **in** a strict scope, with its applicable Type **not** registered as terminal under ANECHOIC-REQU-030. include a registered terminal Type as a control.

**Expected result:** fail the nonterminal fixture with the stable strict-child-coverage diagnostic **and** a non-zero exit. do **not** fail the registered terminal control for missing children alone; retain other applicable authority checks.
