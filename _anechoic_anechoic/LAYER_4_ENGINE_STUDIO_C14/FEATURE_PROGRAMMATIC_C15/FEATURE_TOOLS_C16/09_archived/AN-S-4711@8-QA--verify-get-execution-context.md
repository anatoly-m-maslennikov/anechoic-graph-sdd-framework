---
atom_family: SPEC
atom_id: AN-S-4711
container:
  component: C16
tier: 3
context:
  lens: QA
state:
  status: archived
  version: 8
  updated_at: 2026-10-27 06:04:45 +0400
---
## Summary

Verify GET_EXECUTION_CONTEXT

# Summary

Verify GET_EXECUTION_CONTEXT

## Scope

the GET_EXECUTION_CONTEXT capability for Tool/GET_EXECUTION_CONTEXT.

## Claim

the Evaluation **must** check the GET_EXECUTION_CONTEXT Tool against its declared result **and** Carrier contract using an end-to-end mock Project.

## Details

- exercise exact resolution, unknown or ambiguous identifiers, Workflow Step context, prompt freshness, unrelated-content exclusion, and incomplete-context reporting at the byte budget.
- compare complete expected results with actual results; successful counts alone do **not** establish correctness.
- invoke the real MCP transport for the exposed schema **and** result boundary.
- retain existing RMED Atoms Base Revise behavior, including its initial evidence **and** absence of a saved-output recheck.
