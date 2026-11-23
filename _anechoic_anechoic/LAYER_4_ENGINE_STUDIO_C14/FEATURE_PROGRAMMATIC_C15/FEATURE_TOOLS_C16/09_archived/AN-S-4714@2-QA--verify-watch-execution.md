---
atom_family: SPEC
atom_id: AN-S-4714
container:
  component: C16
tier: 3
context:
  lens: QA
state:
  status: archived
  version: 2
  updated_at: 2026-10-23 01:47:30 +0400
---
## Summary

Verify WATCH_EXECUTION

# Summary

Verify WATCH_EXECUTION

## Scope

the WATCH_EXECUTION capability for Tool/WATCH_EXECUTION.

## Claim

the Evaluation **must** check the WATCH_EXECUTION Tool against its declared result **and** Carrier contract using an end-to-end mock Project.

## Details

- exercise completion, failure, interruption, reconnect replay, cursor validation and Run correlation, timeout, recording acknowledgements, and nonblocking concurrent callers.
- compare complete expected results with actual results; successful counts alone do **not** establish correctness.
- invoke the real MCP transport for the exposed schema **and** result boundary.
- retain existing RMED Atoms Base Revise behavior, including its initial evidence **and** absence of a saved-output recheck.
