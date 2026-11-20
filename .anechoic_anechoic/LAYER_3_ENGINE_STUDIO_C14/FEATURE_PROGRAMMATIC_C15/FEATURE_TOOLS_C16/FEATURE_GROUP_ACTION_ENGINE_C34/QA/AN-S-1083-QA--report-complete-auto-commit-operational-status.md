---
identity:
  atom_id: AN-S-1083
context:
  container:
    component: C34
  tier: 3
  lens: QA
state:
  status: active
  version: 22
  updated_at: 2026-11-02 19:44:26 +0400
---
## Summary

Report complete auto-commit operational status

# Report complete auto-commit operational status

## Claim checked

an Operator can inspect complete current commit-automation transport, service, queue, action, Git-gate, failure, **and** recovery state through one read-only interface.

## Test case

prepare an enabled asynchronous Codex adapter, one live service, queued **and** active actions, one fenced repository lease, one blocked action, one dead letter, partly consumed budgets, an open circuit, **and** prior completed real-change **and** Journal-only actions; invoke integrated status once.

## Acceptance criteria

one schema-versioned result reports Hook activation, service process **and** selected release, admission, queue count **and** bytes, current action **and** phase, pending state, lease, last success **and** failure, budget usage, circuit state, dead letters, receipts, **and** deterministic recovery instructions. the invocation changes no Hook carrier, process, queue item, action state, file, index entry, ref, Journal record, lease, budget, circuit, **or** adapter state.

## Failure disposition

reject the delivery **if** required state is absent, stale, ambiguous, available **only** through Runtime-file inspection, **or** changed by status.
