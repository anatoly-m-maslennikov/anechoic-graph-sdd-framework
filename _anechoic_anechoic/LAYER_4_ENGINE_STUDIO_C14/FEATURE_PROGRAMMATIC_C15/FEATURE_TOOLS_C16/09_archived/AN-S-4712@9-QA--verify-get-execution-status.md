---
atom_family: SPEC
atom_id: AN-S-4712
container:
  component: C16
tier: 3
context:
  lens: QA
state:
  status: archived
  version: 9
  updated_at: 2026-10-27 19:59:36 +0400
---
## Summary

Verify GET_EXECUTION_STATUS

# Summary

Verify GET_EXECUTION_STATUS

## Scope

the GET_EXECUTION_STATUS capability for Tool/GET_EXECUTION_STATUS.

## Claim

the Evaluation **must** check the GET_EXECUTION_STATUS Tool against its declared result **and** Carrier contract using an end-to-end mock Project.

## Details

- exercise running, completed, failed, interrupted, pending Actions, initial check results preserved through fixing, missing Runs, unsupported Action IDs, and recording failure.
- compare complete expected results with actual results; successful counts alone do **not** establish correctness.
- invoke the real MCP transport for the exposed schema **and** result boundary.
- retain existing RMED Atoms Base Revise behavior, including its initial evidence **and** absence of a saved-output recheck.
