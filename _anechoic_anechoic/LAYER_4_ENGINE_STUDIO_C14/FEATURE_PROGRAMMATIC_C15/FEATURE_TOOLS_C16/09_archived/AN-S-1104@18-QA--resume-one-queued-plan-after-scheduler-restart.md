---
atom_family: SPEC
atom_id: AN-S-1104
container:
  component: C16
tier: 3
context:
  lens: QA
state:
  status: archived
  version: 18
  updated_at: 2026-10-27 19:59:33 +0400
---
## Summary

Resume one queued plan after Scheduler restart

# Resume one queued plan after Scheduler restart

## Claim checked

a durable manager-defined plan survives Scheduler **and** service termination.

## Test case

persist one plan with a completed step **and** one newly ready step, terminate the Scheduler **and** manager, restart from the selected installed release, **and** dispatch once.

## Acceptance criteria

the completed step is **not** replayed, exactly the persisted ready step is claimed, its identities **and** digests are preserved, **and** no new transition is inferred.

## Failure disposition

reject recovery **if** work is lost, duplicated, reordered, **or** reconstructed from process memory.
