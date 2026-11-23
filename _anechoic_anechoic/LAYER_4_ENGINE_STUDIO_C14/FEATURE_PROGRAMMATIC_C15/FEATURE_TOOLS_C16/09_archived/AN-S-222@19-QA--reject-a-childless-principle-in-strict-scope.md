---
atom_family: SPEC
atom_id: AN-S-222
container:
  component: C16
tier: 2
context:
  lens: QA
state:
  status: archived
  version: 19
  updated_at: 2026-10-24 11:58:20 +0400
---
## Summary

Reject a childless Principle in strict scope

# Reject a childless Principle in strict scope

## Test case

**Fixture:** leave an Active Principle **without** an active permitted child **in** a strict scope, with its applicable Type **not** registered as terminal under CA-R-030. include a registered terminal Type as a control.

**Expected result:** fail the nonterminal fixture with the stable strict-child-coverage diagnostic **and** a non-zero exit. do **not** fail the registered terminal control for missing children alone; retain other applicable authority checks.
