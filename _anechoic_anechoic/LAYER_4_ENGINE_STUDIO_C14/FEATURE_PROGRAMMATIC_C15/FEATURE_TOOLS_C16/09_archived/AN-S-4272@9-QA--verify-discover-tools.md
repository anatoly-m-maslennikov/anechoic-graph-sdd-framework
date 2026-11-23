---
atom_family: SPEC
atom_id: AN-S-4272
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

Verify DISCOVER_TOOLS

# Summary

Verify DISCOVER_TOOLS

## Scope

the DISCOVER_TOOLS capability for Tool/DISCOVER_TOOLS.

## Claim

the Evaluation **must** check the DISCOVER_TOOLS Tool against its declared result **and** Carrier contract using an end-to-end mock Project.

## Details

- exercise search, pagination, missing implementations, disabled or inactive authority, duplicate identities, malformed YAML, protected paths, and current-source refresh.
- compare complete expected results with actual results; successful counts alone do **not** establish correctness.
- invoke the real MCP transport for the exposed schema **and** result boundary.
- retain existing RMED Atoms Base Revise behavior, including its initial evidence **and** absence of a saved-output recheck.
