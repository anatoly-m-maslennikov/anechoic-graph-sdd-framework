---
atom_family: SPEC
atom_id: AN-S-4713
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

Verify RESUME_EXECUTION_CONTEXT

# Summary

Verify RESUME_EXECUTION_CONTEXT

## Scope

the RESUME_EXECUTION_CONTEXT capability for Tool/RESUME_EXECUTION_CONTEXT.

## Claim

the Evaluation **must** check the RESUME_EXECUTION_CONTEXT Tool against its declared result **and** Carrier contract using an end-to-end mock Project.

## Details

- exercise unfinished check continuation, pending repairs, terminal Runs, stale sources or criteria, retained handoffs, and completed-work exclusion.
- compare complete expected results with actual results; successful counts alone do **not** establish correctness.
- invoke the real MCP transport for the exposed schema **and** result boundary.
- retain existing RMED Atoms Base Revise behavior, including its initial evidence **and** absence of a saved-output recheck.
