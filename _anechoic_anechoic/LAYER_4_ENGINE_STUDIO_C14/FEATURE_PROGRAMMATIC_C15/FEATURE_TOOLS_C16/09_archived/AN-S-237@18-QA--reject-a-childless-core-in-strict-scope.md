---
atom_family: SPEC
atom_id: AN-S-237
container:
  component: C16
tier: 2
context:
  lens: QA
state:
  status: archived
  version: 18
  updated_at: 2026-10-24 08:53:16 +0400
---
## Summary

Reject a childless Core in strict scope

# Reject a childless Core in strict scope

## Test case

**Fixture:** leave an Active Core **without** an active permitted child **in** a strict scope, with its applicable Type **not** registered as terminal under CA-R-030. include a registered terminal Type as a control.

**Expected result:** fail the nonterminal fixture with the stable strict-child-coverage diagnostic **and** a non-zero exit. do **not** fail the terminal control for missing children alone; retain other applicable authority checks.
