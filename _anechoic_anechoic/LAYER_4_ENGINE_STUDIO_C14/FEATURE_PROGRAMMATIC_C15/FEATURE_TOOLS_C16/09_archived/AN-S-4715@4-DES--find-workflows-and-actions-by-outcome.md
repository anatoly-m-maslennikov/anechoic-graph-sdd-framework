---
atom_family: SPEC
atom_id: AN-S-4715
container:
  component: C16
tier: 3
context:
  lens: DES
state:
  status: archived
  version: 4
  updated_at: 2026-10-24 11:58:20 +0400
---
## Summary

Find Workflows and Actions by outcome

# Summary

Find Workflows and Actions by outcome

## Scope

the DISCOVER_OPERATIONS capability for Tool/DISCOVER_OPERATIONS.

## Claim

the DISCOVER_OPERATIONS Tool **must** return a ranked, bounded selection of active Workflow and Action definitions matching the requested outcome and filters.

## Details

- implement the methodology Action CA-O-113-PROJECT_CONFIGURATION-ACTION--discover-operations.
- accept a query, Workflow or Action kind, Scope Unit and execution-kind filters, offset, and result limit; return summaries, definition bindings, and implementation availability.
- preserve the Operator's choice of what **to** execute; discovery, context retrieval, **and** observation provide capabilities.
- bounded **or** unavailable evidence **must** remain explicit **rather than** establish a successful assessment.
