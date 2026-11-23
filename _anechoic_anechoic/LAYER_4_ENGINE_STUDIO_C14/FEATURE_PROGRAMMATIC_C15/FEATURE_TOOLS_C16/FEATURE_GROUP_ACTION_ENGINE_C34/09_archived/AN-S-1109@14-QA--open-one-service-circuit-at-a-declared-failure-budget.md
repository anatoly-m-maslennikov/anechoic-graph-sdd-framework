---
atom_family: SPEC
atom_id: AN-S-1109
container:
  component: C34
tier: 3
context:
  lens: QA
state:
  status: archived
  version: 14
  updated_at: 2026-10-24 11:58:20 +0400
---
## Summary

Open one service circuit at a declared failure budget

# Open one service circuit at a declared failure budget

## Claim checked

automatic recovery is bounded **and** integrity-sensitive failures require Operator action.

## Test case

exhaust one measured transient restart budget, **then** separately inject governance, Journal, staging, ambiguous Git, **and** lease-integrity failures.

## Acceptance criteria

transient recovery stops at the declared budget **and** opens a visible circuit. **every** integrity-sensitive failure pauses autonomous dispatch immediately, preserves accepted state, **and** reports deterministic Operator recovery instructions. no unconditional auto-resume occurs.

## Failure disposition

reject the service **if** it loops, hides budget use, drops work, **or** retries an integrity-sensitive failure autonomously.
