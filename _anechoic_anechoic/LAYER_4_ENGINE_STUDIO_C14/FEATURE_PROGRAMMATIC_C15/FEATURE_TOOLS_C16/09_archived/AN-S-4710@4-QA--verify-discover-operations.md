---
atom_family: SPEC
atom_id: AN-S-4710
container:
  component: C16
tier: 3
context:
  lens: QA
state:
  status: archived
  version: 4
  updated_at: 2026-10-24 11:58:20 +0400
---
## Summary

Verify DISCOVER_OPERATIONS

# Summary

Verify DISCOVER_OPERATIONS

## Scope

the DISCOVER_OPERATIONS capability for Tool/DISCOVER_OPERATIONS.

## Claim

the Evaluation **must** check the DISCOVER_OPERATIONS Tool against its declared result **and** Carrier contract using an end-to-end mock Project.

## Details

- exercise Workflow and Action separation, Agentic or Programmatic filters, inactive definitions, duplicate identifiers, no results, and declared but unavailable implementations.
- compare complete expected results with actual results; successful counts alone do **not** establish correctness.
- invoke the real MCP transport for the exposed schema **and** result boundary.
- retain existing RMED Atoms Base Revise behavior, including its initial evidence **and** absence of a saved-output recheck.
